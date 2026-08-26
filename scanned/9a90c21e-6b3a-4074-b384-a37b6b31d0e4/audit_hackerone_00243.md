# [M] GraphQL node interface for ActiveResource models lacks encoding for resource identifier, enabling parameter injection in Payments backend

## Summary
Severity: Medium (CVSS 6.1)
Program: HackerOne
Weakness: Information Disclosure
Reporter: jobert
State: resolved
Disclosed: 2020-05-11T17:53:34.131Z
CVE: CVE-2020-8151
Source: https://hackerone.com/reports/800231

## Details
HackerOne exposes a small number of ActiveResource objects through its GraphQL `node` interface. [ActiveResource](https://github.com/rails/activeresource) objects use HTTP as transport layer in order to fetch data. Four of these models, `TaxForm`, `Payout`, `Payment`, and `PayoutPreference` are fetched from an internal Payments backend system with a REST interface. Due to the lack of encoding the resource identifier, it is possible to inject additional parameters and point a `find` call to a difference resource endpoint.

# Proof of concept
Consider the following GraphQL query:

```
query {
  node(id: "gid://hackerone/PaymentsLibrary::Payment/1") {
    ... on User { 
      id
    }
  }
}
```

**Note**: it's important to note that the model the node identifier would return does **not** correspond with the expected GraphQL type. This is important for the exploit later in the report. This query would send the following HTTP request to HackerOne's Payments backend:

```
GET /payments/1 HTTP/1.1
...
```

Because ActiveResource does not have an opinion on identifiers, it won't encode it (e.g. it doesn't raise an exception when a string is passed instead of an integer). This means that the following GraphQL query:

```
query {
  node(id: "gid://hackerone/PaymentsLibrary::Payment/something") {
    ... on User {
      id
    }
  }
}
```

Will result in the following HTTP request:

```
GET /payments/something HTTP/1.1
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/800231_
