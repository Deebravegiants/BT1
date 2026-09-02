### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while `shop` (and `topic`, `api_version`, `webhook_id`) are read from separate, unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then trusts `request.shop` when constructing `WebhookMetadata` passed to the app's handler, without ever confirming that the signed body actually belongs to that shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never mixed into the signable string: [2](#0-1) 

`Utils::HmacValidator.validate` verifies `verifiable_query.hmac` against `verifiable_query.to_signable_string` only — so it authenticates the body bytes, not the shop header: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` to build the metadata handed to the app's own webhook handler: [4](#0-3) 

Because the same `api_secret_key` is shared across every shop that has installed the app, any merchant who has legitimately installed the app can receive a genuine, validly-signed webhook for their own shop (with a valid HMAC over the raw body) and replay it to the app's webhook endpoint after altering only the `shopify-shop-domain` header to point at a *different* installed shop. The HMAC still validates because the header is not part of the signed content, yet `WebhookMetadata.shop` — the value host applications use to look up which tenant's data/session the payload belongs to — now falsely identifies a victim shop. This breaks the intended binding: `shop asserted in WebhookMetadata == shop that actually produced/authorized the signed body`, enabling one tenant to inject attacker-controlled webhook data attributed to another tenant (cross-tenant data confusion/injection).

### Impact Explanation
This crosses a tenant boundary: a webhook payload's shop attribution is not authenticated, so an unprivileged (but app-installed) actor can make the host application process arbitrary body content while it believes the data belongs to a different, unrelated shop. Host applications built on this gem's documented `WebhookMetadata.shop` field (as intended for use, see `Registry.process`) will act on forged tenant identity, matching the Critical "cross-tenant access" category.

### Likelihood Explanation
High. No secret material is required beyond what any legitimate app-installing merchant already possesses (their own valid inbound webhook traffic). The attack requires only capturing/replaying one real webhook delivery to their own shop and rewriting a single HTTP header before resending it to the app's public webhook endpoint — the HMAC check in `Registry.process`/`HmacValidator.validate` places no constraint on that header.

### Recommendation
Bind the `shop` (and ideally `topic`/`api_version`/`webhook_id`) values into the HMAC-verified content, or otherwise cryptographically tie the header-derived shop to the signed body (e.g., include the shop domain in `to_signable_string`, or cross-check it against a shop value embedded in the signed payload) before it is exposed via `WebhookMetadata` to consuming applications.

### Proof of Concept
1. Attacker's own shop `attacker.myshopify.com` (a real, installed shop) receives a legitimate webhook from Shopify, with headers:
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - `x-shopify-hmac-sha256: <valid HMAC of raw body>`
   - raw body: `{"id": 1, ...}`
2. Attacker resends this exact body and HMAC to the app's webhook endpoint, changing only the header:
   - `x-shopify-shop-domain: victim.myshopify.com`
3. `ShopifyAPI::Webhooks::Request.new` parses this into an object whose `shop` is `"victim.myshopify.com"`.
4. `Utils::HmacValidator.validate(request)` succeeds because it only checks `@raw_body` against the shared `api_secret_key` — the shop header is irrelevant to the signature. [5](#0-4) 
5. The app's handler executes with `WebhookMetadata.shop == "victim.myshopify.com"` even though the payload was actually attacker-supplied, causing the host application to associate attacker data with the victim tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
