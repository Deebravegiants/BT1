### Title
Webhook `shop` (tenant) attribution is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then blindly trusts the unauthenticated `shopify-shop-domain` header to attribute the payload to a specific merchant. Because the HMAC secret (`Context.api_secret_key`, the app's `client_secret`) is the same for every shop that installs the app, and the signed bytes never include the shop identifier, a genuinely signed webhook body obtained from one shop can be replayed to the same endpoint with the `shop-domain` header swapped to a different, victim shop, and it will still pass validation.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Webhooks::Request#shop` simply reads the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is not part of the signable string at all: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately builds `WebhookMetadata` using `request.shop`, `request.topic`, and `request.parsed_body`, with no check binding the shop header to the signed body: [3](#0-2) 

`HmacValidator.validate` computes `HMAC-SHA256(secret, to_signable_string)` where `secret` is `Context.api_secret_key` — the single, app-wide `client_secret`, identical for every merchant that installs the app: [4](#0-3) 

The binding that should hold is:
`hmac_valid(body, secret) == true` implies `shop_header == shop_that_actually_produced(body)`

But since `to_signable_string` excludes the shop header, the equality breaks: `hmac_valid(body, secret)` is true for *any* shop header value paired with that exact `body`, because the secret is shared across all tenants of the app and the signed bytes never encode which tenant sent it.

**Exploit path:** an unprivileged attacker installs the target app on their own (attacker-controlled) Shopify development/test store — a normal, permitted action for any public app. Shopify delivers a legitimately HMAC-signed webhook to the app's endpoint with `shopify-hmac-sha256` computed over the body and `shopify-shop-domain: attacker-shop.myshopify.com`. The attacker captures this valid `(body, hmac)` pair, then replays it to the app's webhook endpoint while substituting `shopify-shop-domain: victim-shop.myshopify.com`. `HmacValidator.validate` still returns `true` because the body and HMAC are unchanged and the secret is the same for all shops. `Registry.process` then invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the application to act on attacker-supplied data attributed to the victim tenant.

### Impact Explanation
This breaks the tenant boundary the library is expected to enforce: the app's business logic keyed on `WebhookMetadata#shop` (e.g., updating per-shop records, gating features, mutating subscription/billing state, or triggering the app's write-side logic for that shop) can be invoked by an attacker for a shop they do not own, using the attacker's own legitimately-signed payload as the vehicle. This is a cross-tenant access vector attributable directly to how this gem structures webhook verification (`hmac(body)` treated as sufficient authentication, `shop` treated as a trusted attribute despite being outside the signed bytes).

### Likelihood Explanation
Any developer/attacker can install a public app on their own store to obtain a validly signed webhook of a chosen topic/body, then trivially replay the HTTP request with one header changed. No secrets, tokens, or elevated access are required — only the ability to receive one's own app webhooks and issue an HTTP request to the app's public webhook endpoint.

### Recommendation
Do not treat the `shop` (or `topic`/`webhook-id`) header as trusted merely because the body HMAC validates. Either:
- Incorporate the shop domain into the value that is cryptographically verified (e.g., require the app to independently confirm the shop is a known, currently-installed shop with a valid stored session/access token before trusting `request.shop`), or
- Document explicitly, and enforce in `Registry.process`, that HMAC validation only proves the payload came from Shopify for this `client_secret`, not that it originated for the shop named in the header, and require callers to cross-check `request.shop` against their own installed-shops store prior to acting on the webhook.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Attacker triggers an event so Shopify sends a webhook, e.g. body `{"id":1,...}` with headers:
   - `shopify-hmac-sha256: <valid HMAC over the body using the app's client_secret>`
   - `shopify-shop-domain: attacker-shop.myshopify.com`
3. Attacker replays the identical body and HMAC header to the same webhook endpoint, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-190`) calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `OpenSSL::HMAC.hexdigest(secret, raw_body)` against the unchanged body and hmac.
5. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: attacker_controlled_body, ...)`, causing the app to process attacker-controlled data under the victim shop's identity.

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
