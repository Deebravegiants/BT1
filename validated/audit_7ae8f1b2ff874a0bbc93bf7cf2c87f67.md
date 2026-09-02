### Title
Webhook `shop` identity is trusted by the handler without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook purely by checking that the HMAC of the raw body matches the app's secret, then dispatches to the handler using a `shop` value taken from an HTTP header that is never included in the signed material.

### Finding Description
The webhook `Request` object exposes `shop` from the `shopify-shop-domain`/`x-shopify-shop-domain` header: [1](#0-0) 

The HMAC that gets verified, however, is computed only over the raw body: [2](#0-1) 

`HmacValidator.validate` checks `verifiable_query.hmac` against `HMAC(secret, verifiable_query.to_signable_string)`, i.e. `HMAC(secret, raw_body)` for webhook requests: [3](#0-2) 

`Registry.process` uses this same result to authorize dispatch, and passes the *unauthenticated* `request.shop` value straight into `WebhookMetadata`, which the app's handler is documented to trust as "The shop domain of the webhook": [4](#0-3) [5](#0-4) 

The identity binding that should hold is: `shop-domain header == shop cryptographically bound inside the signed payload`. In this gem it instead holds only: `HMAC(secret, raw_body) == valid`, while `shop` is asserted out-of-band via an unauthenticated header. Because the app-level `api_secret_key` (and therefore the resulting HMAC) is identical for every shop that has installed the same app, a valid `(raw_body, hmac)` pair obtained from a webhook delivered for one authorized tenant (e.g. the attacker's own shop, which they legitimately control and can freely install the app on) remains cryptographically valid when replayed to the app's webhook endpoint with the `shopify-shop-domain` header changed to a different, victim tenant's `myshopify.com` domain (a value that is public/guessable). `Registry.process` will accept the request (HMAC over body is still correct) and hand the handler a `WebhookMetadata` claiming `shop: <victim>` together with the attacker's own body content.

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce for webhook authenticity: an app built on this gem's documented `Registry.process`/`WebhookMetadata` contract can be made to process attacker-supplied webhook data under an arbitrary victim shop's identity, since the gem gives the host application no cryptographic assurance that `data.shop` corresponds to the shop that actually produced `data.body`. Any handler logic that keys per-tenant state (session lookups, billing, inventory writes, deduplication tables, feature flags) off `data.shop` can be attributed to the wrong tenant — a cross-tenant integrity issue arising directly from this gem's own verification code, not from host misuse.

### Likelihood Explanation
Exploitation only requires the attacker to install the app on a shop they control (ordinary unprivileged action for a public app) in order to obtain one genuinely-signed `(raw_body, hmac)` pair, then POST it directly to the app's public webhook endpoint with a forged `shopify-shop-domain` header. No access to `api_secret_key`, access tokens, or the victim's credentials is required — only the victim shop's domain name, which is typically public. This is a low-effort, network-only replay against the gem's own verification primitive.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook-id`) into the value that is HMAC-verified, or otherwise cross-check the header-derived `shop` against session/installation state (e.g., confirm the shop is a currently installed shop and that the specific `webhook-id` hasn't been seen for a different shop) before trusting `WebhookMetadata#shop` in `Registry.process`. At minimum, the gem should not present the header-derived `shop` as verified data once `Utils::HmacValidator.validate` has returned true, and documentation in `docs/usage/webhooks.md` should make explicit that `data.shop` is not cryptographically authenticated by the HMAC check.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`, receiving a legitimately signed webhook: `raw_body = B`, header `shopify-hmac-sha256 = HMAC(secret, B)` (secret is the app's single `api_secret_key`, shared across all installs).
2. Attacker replays this exact `(B, hmac)` pair directly to the app's public webhook endpoint but sets `shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (no correlation between `shop` header and `hmac` is enforced) — `lib/shopify_api/webhooks/request.rb:45-63`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because `B` and its HMAC are genuinely correct — `lib/shopify_api/webhooks/registry.rb:188-190`, `lib/shopify_api/utils/hmac_validator.rb:12-22`.
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's data>, ...)` and processes attacker-controlled data as though it originated from the victim shop — `lib/shopify_api/webhooks/registry.rb:198-199`.

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
