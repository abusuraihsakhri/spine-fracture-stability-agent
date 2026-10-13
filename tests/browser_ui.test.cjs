// Dependency-free behavioral smoke tests for the standalone browser calculator.
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const html = fs.readFileSync("web/index.html", "utf8");
const match = html.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(match, "Expected inline calculator script");
assert.ok(!html.includes("fetch("), "Static calculator must not send input to a server");

class Element {
  constructor(id = "") {
    this.id = id;
    this.children = [];
    this.value = "";
    this.textContent = "";
    this.checked = false;
    this.hidden = false;
    this.disabled = false;
    this.listeners = {};
  }
  replaceChildren() { this.children = []; this.value = ""; }
  appendChild(child) { this.children.push(child); }
  addEventListener(name, fn) { this.listeners[name] = fn; }
  change() { this.listeners.change(); }
}
const elements = new Map();
const element = id => {
  if (!elements.has(id)) elements.set(id, new Element(id));
  return elements.get(id);
};
element("scale").value = "TLICS";
const document = {
  getElementById: element,
  createElement: () => new Element()
};
vm.runInNewContext(match[1], {document, console, setTimeout, URL, Blob});
assert.equal(element("download").disabled, true);
assert.equal(element("score").textContent, "—");
element("morphology").value = "burst";
element("ligament").value = "indeterminate";
element("neurologic").value = "intact";
element("neurologic").change();
assert.equal(element("score").textContent, "4");
assert.equal(element("p-morphology").textContent, "2");
assert.equal(element("p-ligament").textContent, "2");
assert.equal(element("download").disabled, false);

element("scale").value = "SLIC";
element("scale").change();
assert.equal(element("download").disabled, true);
element("morphology").value = "compression";
element("ligament").value = "indeterminate";
element("neurologic").value = "complete_cord";
element("neurologic").change();
assert.equal(element("score").textContent, "4");
element("modifier").checked = true;
element("modifier").change();
assert.equal(element("score").textContent, "5");
element("neurologic").value = "intact";
element("neurologic").change();
assert.equal(element("score").textContent, "2");
assert.equal(element("modifier").disabled, true);
assert.equal(element("modifier").checked, false);
console.log("Browser calculator smoke tests passed");
