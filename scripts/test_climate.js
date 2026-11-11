#!/usr/bin/env node
"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const source = fs.readFileSync("app.js", "utf8");
const start = source.indexOf("function seasonForYear(");
const end = source.indexOf("async function fetchHistoricalDaily(", start);
assert.ok(start >= 0 && end > start, "season and climate summary helpers must exist");

const helperSource = source.slice(start, end);
const sandbox = {};
vm.runInNewContext(
  helperSource + "\nthis.__climateTest = { seasonForYear, dateKey, summarizeClimateSeason };",
  sandbox,
  { timeout: 1000 }
);

const { seasonForYear, dateKey, summarizeClimateSeason } = sandbox.__climateTest;
const season = seasonForYear(2010, "10-01", "06-30");
assert.equal(dateKey(season.start), "2009-10-01");
assert.equal(dateKey(season.end), "2010-06-30");

function makeDaily(startDate, endDate, options = {}) {
  const byDate = new Map();
  const cursor = new Date(startDate);
  while (cursor <= endDate) {
    const key = cursor.toISOString().slice(0, 10);
    const day = Math.round((cursor - startDate) / 86400000);
    byDate.set(key, {
      temp: options.missingTemp?.has(day) ? null : 12 + (day % 8) / 10,
      rain: options.missingRain?.has(day) ? null : (day % 4) / 2,
      et0: options.missingEt0?.has(day) ? null : 2.5
    });
    cursor.setUTCDate(cursor.getUTCDate() + 1);
  }
  return byDate;
}

const complete = makeDaily(season.start, season.end, {
  missingEt0: new Set(Array.from({ length: 150 }, (_, i) => i))
});
const completeSummary = summarizeClimateSeason(complete, season.start, season.end);
assert.equal(completeSummary.usable, true, "temperature/rain coverage should pass when ET0 is incomplete");
assert.equal(completeSummary.et0, null, "incomplete ET0 must be optional");
assert.ok(completeSummary.coverage >= 0.8);
assert.ok(completeSummary.tempCoverage >= 0.99);
assert.ok(completeSummary.rainCoverage >= 0.99);

const missingRainDays = new Set(Array.from({ length: 70 }, (_, i) => i));
const incomplete = makeDaily(season.start, season.end, { missingRain: missingRainDays });
const incompleteSummary = summarizeClimateSeason(incomplete, season.start, season.end);
assert.equal(incompleteSummary.usable, false, "season with less than 80% rainfall coverage must be rejected");

const partialEt0 = makeDaily(season.start, season.end, {
  missingEt0: new Set(Array.from({ length: 80 }, (_, i) => i))
});
const partialEt0Summary = summarizeClimateSeason(partialEt0, season.start, season.end);
assert.equal(partialEt0Summary.usable, true, "partial ET0 must not discard otherwise usable climate years");
assert.equal(partialEt0Summary.et0, null);

console.log("PASS climate test: wheat season dates, 80% core coverage, and optional ET0 behavior");
