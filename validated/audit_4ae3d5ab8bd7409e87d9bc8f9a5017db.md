### Title
Webhook shop-tenant binding is unauthenticated — `shop` header is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` claims to "verify the request did indeed come from Shopify" before invoking the app's handler, but the HMAC signature it validates covers only the raw request body — never the `shop`, `topic`, `webhook_id`, or `api_version` values that are taken directly from unauthenticated HTTP headers and handed to the app as trusted, tenant-identifying data.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0)  while `#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the body: [2](#0-1) 

`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (the body only) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` treats a passing HMAC check as full authentication of the entire request and then forwards the unauthenticated `request.shop` value into `WebhookMetadata` for the app handler: [4](#0-3) 

The identity binding that should hold is: `shop header == shop that the HMAC-signed body actually originated from`. Because the HMAC secret (`api_secret_key`) is the same for every shop that has installed a given app, and the signature covers only the body bytes, this equality is never enforced. An attacker who controls a shop with the target app installed receives genuine webhook deliveries with valid `(body, hmac)` pairs for their own shop. They can replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds because it never looks at the shop header, and `Registry.process` calls the handler with `shop: "<victim>.myshopify.com"` attached to attacker-controlled body content.

The gem's own documentation reinforces the false trust: `docs/usage/webhooks.md` states that `Registry.process` "will verify the request did indeed come from Shopify" and shows the exact handler pattern (`shop_domain: data.shop`) that a host application is expected to follow, with `shop` documented simply as "The shop domain of the webhook" — with no caveat that it is unauthenticated.

### Impact Explanation
This breaks the tenant boundary this gem is responsible for maintaining: the shop identity delivered to the app's webhook handler for a signature-verified payload can be attacker-chosen while the payload content is also attacker-influenced (any body they can get legitimately signed for their own shop, including topics like `app/uninstalled`, `customers/data_request`, `shop/update`, etc.). A host application that follows the gem's documented contract (using `data.shop` to select which tenant's records to update, revoke, or notify) can be made to apply attacker-supplied webhook data to a different merchant's tenant — a cross-tenant data integrity/confidentiality violation reachable by any unprivileged internet user who has installed the app on a shop they control, with no secrets beyond a webhook they legitimately received.

### Likelihood Explanation
High reachability: installing a Shopify app on a free/dev store is trivial for an attacker, giving them a stream of validly-HMAC-signed webhook bodies for arbitrary standard topics. Forging the `shop-domain` header on the replayed HTTP request requires no additional secret. The only precondition is that the host app trusts `WebhookMetadata#shop` as the gem instructs it to.

### Recommendation
Bind the shop identity into the signed payload verification, e.g. require and verify a per-shop-bound value (or document that `shop` is untrusted and callers must independently confirm the shop is one they have an active session/install for and correlate the topic/webhook_id via Shopify's API before trusting it), or include the shop domain in the HMAC computation input so the signature commits to the header value the app relies on.

### Proof of Concept
1. Attacker creates a development store and installs the target app, receiving legitimate webhook POSTs like:
```
POST /callback/orders/create
x-shopify-topic: orders/create
x-shopify-hmac-sha256: <valid-for-body>
x-shopify-shop-domain: attacker-shop.myshopify.com
Body: {"id": 1, "note": "..."}
```
2. Attacker replays the identical body and `x-shopify-hmac-sha256` value to the same endpoint, but changes:
```
x-shopify-shop-domain: victim-shop.myshopify.com
```
3. `ShopifyAPI::Webhooks::Registry.process` computes the HMAC over the body only [5](#0-4) , which matches, and calls the app handler with `shop: "victim-shop.myshopify.com"` [6](#0-5) , causing the host app to process attacker-controlled data under the victim shop's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```
