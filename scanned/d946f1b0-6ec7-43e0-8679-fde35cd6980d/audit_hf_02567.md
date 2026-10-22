# [M] Sandwich attack for turnEmpirePointPriceDown()

## Summary
Severity: Medium
Contest weight: 0.2204
Dataset id: 13797
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Admins call turnEmpirePointPriceDown() and reduce the price of an empire's points: function turnEmpirePointPriceDown(EEmpire _empire) internal { P_PointConfigData memory config = P_PointConfig.get(); uint256 newPointPrice = Empire.getPointPrice(_empire); if (newPointPrice >= config.minPointPrice + config.pointGenRate) { newPointPrice -= config.pointGenRate; } else { newPointPrice = config.minPointPrice; Empire.setPointPrice(_empire, newPointPrice); HistoricalPointPrice.set(_empire, block.timestamp, newPointPrice); The issue is that the code subtracts an absolute value from the empire's point's price. So if the price of the points was lower then the percentage price decrease would be higher and users can use this to profit from price decrease by sandwich attacks. Users can't buy points directly and they need to buy override but the result is the same. Users can time their override buys with the admin's transaction and perform the sandwich attack to benefit from the admin's transactions. This is the POC: (buying points means buying some override which results in buying points) 1. Suppose an empire's point's price is 100. 2. User1 has 50 points in that empire and if he buys one more token it would cost 100. 3. Admins call turnEmpirePointPriceDown() to reduce the price by 10 units. 4. User1 would perform a sandwich attack for the admin's transaction and first he would sell his 50 points so the price would be decreased to 50. 5. Then the admin's transaction would be executed and the point's price would be 49. 6. Now User1 would buy 1 token with the price of 50 units and buy the sold 50 points with their sell price. 7. In the end user was able to buy 1 token with a price of 50 instead of 100.

## Recommendation
Use percentage or value( point * price ) based on price decrease or decrease the price over time.
