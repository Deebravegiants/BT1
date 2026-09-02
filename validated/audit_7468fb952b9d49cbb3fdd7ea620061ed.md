I have enough evidence to confirm the finding.

### Title
Webhook shop identity is not covered by the HMAC signature, allowing a malicious merchant to forge the source shop of a webhook - ([File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw body, then trusts the `shop-domain` HTTP header — which is never included in that signature — as the tenant identity passed to the app's handler.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
and `#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the signed bytes: [2](#0-1) 

`Registry.process` validates only the HMAC of the request (i.e., of `raw_body`) and then immediately hands `request.shop` to the registered handler as the authoritative tenant identifier: [3](#0-2) 

The generic `HmacValidator.validate` / `validate_signature` only ever checks `verifiable_query.to_signable_string` against the secret — it has no knowledge of, and does not defend, any field that isn't included in that string: [4](#0-3) 

This breaks the identity binding that the gem's own webhook-processing flow relies on: `request.shop == the shop whose HMAC secret produced request.hmac for this body`. Before an attack, this equality naturally holds because Shopify computes and delivers both the body, its HMAC, and the shop header together for a given shop's webhook event. After the attack, the header can be swapped for an arbitrary value while `raw_body`/`hmac` stay a valid, matching pair — the equality no longer holds — yet `Utils::HmacValidator.validate(request)` still returns `true` because it never inspects `shop`.

Since a webhook signing secret (`Context.api_secret_key`, i.e., the app's `client_secret`) is shared across every shop that installs the app, any unprivileged user can install the app on their own store (a normal, unprivileged action), receive a legitimately-signed webhook body+HMAC pair from Shopify for their own store, and then replay that exact `raw_body`/`hmac` pair to the app's webhook endpoint while substituting the `shop-domain` header with a victim shop's domain. `Registry.process` will accept it as valid and dispatch it to the app's handler tagged with the forged `shop`, in `WebhookMetadata`: [5](#0-4) 

### Impact Explanation
Because `WebhookHandler` implementations in host apps are documented and expected to key stored records (orders, customers, redact requests, etc.) by `data.shop`, an attacker can inject data attributed to an arbitrary victim shop into per-tenant storage, or trigger tenant-scoped side effects (e.g. GDPR `customers/redact`, `shop/redact` mandatory webhooks) against a shop they do not control. This is a cross-tenant confusion/access vulnerability rooted entirely in this gem's failure to bind the authenticated bytes (`raw_body`) to the claimed tenant (`shop-domain` header) before dispatching to handlers.

### Likelihood Explanation
Likelihood is high for any host app that trusts `WebhookMetadata#shop` from a processed webhook as the tenant key (the intended and documented usage). The only prerequisite is that the attacker can install the target app on a shop they control (an ordinary, unprivileged action) to obtain one legitimately-signed body/HMAC pair, and can send arbitrary HTTP requests to the app's public webhook endpoint (also ordinary/unprivileged) with a forged `shop-domain` header.

### Recommendation
Bind the shop identity into the value that is cryptographically verified before it is trusted, for example by including `topic`, `shop-domain`, and `api-version` headers in the signed material used by `to_signable_string`, or by requiring host apps to cross-check `request.shop` against the shop-specific session/webhook registration they expect for that endpoint before invoking the handler, rather than trusting the raw header once body-HMAC validation succeeds.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) so Shopify sends a POST to the app's webhook endpoint with headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid hmac of raw_body>`, and body `raw_body`.
2. Capture `raw_body` and the `X-Shopify-Hmac-Sha256` value from that legitimate delivery.
3. Resend an HTTP POST to the same app webhook endpoint with the identical `raw_body` and `X-Shopify-Hmac-Sha256`, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` returns `true` (only `raw_body` is checked) per [1](#0-0) , and `Registry.process` dispatches to the handler with `shop: "victim-shop.myshopify.com"` per [3](#0-2) , causing the app to act on attacker-supplied data as if it originated from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
