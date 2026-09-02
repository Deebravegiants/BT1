I have enough evidence now to finalize the analysis.

### Title
Webhook `shop`, `topic`, and `webhook-id` headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` authenticates nothing but the JSON body bytes. The `shop`, `topic`, `webhook-id`, and `api-version` values are read straight from HTTP headers, which are never part of the HMAC-signed data, yet `Registry.process` uses this unauthenticated `shop` value to build the `WebhookMetadata` handed to the host app's handler.

### Finding Description
`Registry.process` gates on HMAC validity and then trusts `request.shop`, `request.topic`, and `request.webhook_id` to construct `WebhookMetadata`: [1](#0-0) 

The HMAC check only proves that `@raw_body` was signed with the app's `api_secret_key`: [2](#0-1) 

But `shop`, `topic`, and `webhook_id` are pulled from headers that are completely outside that signed string: [3](#0-2) 

and `HmacValidator` only ever compares `verifiable_query.hmac` against a signature computed from `to_signable_string` (the body): [4](#0-3) 

The equality being broken is: **"shop that the body's HMAC was actually generated for" ≠ "shop the gem reports to the handler."** Because the `api_secret_key` is the app's single client secret shared across every merchant/shop that has installed the app (not a per-shop secret), any merchant who installs the app can obtain a validly-signed `(raw_body, hmac)` pair from their own legitimate webhook deliveries. That merchant can then replay the exact same body+HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`/`x-shopify-webhook-id`) header to name a victim shop. `Utils::HmacValidator.validate` still returns `true` (it never looks at headers), so `Registry.process` happily dispatches the tampered `WebhookMetadata` with `shop: <victim shop>` to the host application's handler.

### Impact Explanation
This breaks the tenant-identity binding "authenticated shop == acted-upon shop" that host applications rely on to route webhook data to the correct tenant record/session. A malicious merchant of Shop A can inject data attributed to Shop B into the app's webhook processing pipeline (e.g., trigger `customers/redact`-style or order-mutation handlers against a shop they don't own, or poison a victim's cached data keyed by shop domain), which is a cross-tenant data-integrity violation — Critical severity per the cross-tenant access category, since it requires no possession of another tenant's credentials and only the attacker's own valid webhook traffic.

### Likelihood Explanation
Any developer/merchant with a working installation of the app can generate arbitrary numbers of legitimately-signed webhook deliveries (by triggering events on their own store) and then replay them with a forged shop header using an ordinary HTTP client — no cryptographic secret needs to be discovered, no MITM/TLS interception is required, and the request goes straight to the app's public webhook endpoint. This is fully unprivileged-internet-user reachable.

### Recommendation
Bind the HMAC to shop-identifying and routing metadata, not just the body: include `shop`, `topic`, and `webhook_id` in the signed string (or independently verify that `body`'s embedded shop-identifying fields, e.g. resource `shop_id` returned by Shopify's Admin API, match the header-reported `shop`) before constructing `WebhookMetadata` in `Registry.process`. At minimum, document loudly that `request.shop` is unauthenticated and host apps must independently verify shop ownership of the referenced resource before trusting it.

### Proof of Concept
1. App merchant "Attacker Shop" (`attacker.myshopify.com`) has legitimately installed the target app and receives a real webhook delivery for `orders/create`, giving them a genuine `(raw_body, x-shopify-hmac-sha256)` pair signed with the app's shared `api_secret_key`.
2. Attacker replays this exact `raw_body` and `x-shopify-hmac-sha256` value to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and any desired `x-shopify-topic`/`x-shopify-webhook-id`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the HMAC [5](#0-4) .
4. `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is built with `shop == "victim-shop.myshopify.com"` and dispatched to the host app's handler, causing the app to process attacker-controlled order data as if it belonged to the victim shop [6](#0-5) .

### Citations

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
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
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
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
