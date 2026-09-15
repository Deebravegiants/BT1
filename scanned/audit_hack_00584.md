# [H] Kame Aggregator incident: Kame Aggregator suffered an exploit due to a design flaw in the swap() function, which allowed arbitrary executor calls. This vuln

## Summary
Severity: High
Target: Kame Aggregator
Loss: $ 1,320,000
Attack method: Contract Vulnerability
Published: 2025-09-12
Source: https://kameagg.substack.com/p/post-mortem-kame-aggregator-exploit
Type: slowmist-incident

## Details
Kame Aggregator suffered an exploit due to a design flaw in the swap() function, which allowed arbitrary executor calls. This vulnerability enabled attackers to transfer tokens authorized to the AggregationRouter by users, particularly those with unlimited or oversized approvals. The total value of affected assets was approximately $1.32 million, of which around $946,000 was recovered by the Kame team from the primary exploiter, and about $22,000 was recovered by white-hat hackers.
