### Title
Webhook Shop-Domain Header Not Bound to HMAC Signature Enables Cross-Tenant Spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body, then dispatches to the app's handler using the `shop` (and `topic`/`webhook_id`) values read directly from HTTP headers that are never included in the signed material. Because the app's `client_secret` (`api_secret_key`) is shared across every shop that has installed the app, any merchant/tenant can capture the (valid body, valid HMAC) pair from a genuine webhook delivered to their own shop and replay it to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` header, causing the handler to process the payload under a different tenant's identity.

### Finding Description
The identity binding that should hold is:
`shop attributed to a processed webhook == shop the HMAC-signed bytes actually originated from`

`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are all pulled straight from HTTP headers, none of which are part of `to_signable_string`: [2](#0-1) 

`HmacValidator.validate` verifies the `hmac` header against `to_signable_string` (i.e., only the raw body) using the app's `api_secret_key`: [3](#0-2) 

`Registry.process` performs exactly this body-only HMAC check, then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) 

Because `api_secret_key` is a single, app-wide secret shared by all installed shops (not a per-shop secret), any shop that has installed the app can generate/receive a webhook whose body+HMAC pair is fully valid for that shared secret. That attacker-controlled tenant can then resend the identical `raw_body` and `hmac-sha256` header to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. `HmacValidator.validate` still succeeds (it never inspected the header), and `Registry.process` forwards `shop: request.shop` — the forged value — to the handler as if the payload legitimately belongs to the spoofed shop.

### Impact Explanation
Any app handler that uses `WebhookMetadata#shop` to look up tenant records, apply state changes (e.g., process `orders/paid`, `app/uninstalled`, GDPR redact topics), or otherwise act on behalf of "the shop that sent this webhook" can be tricked into performing that action against a shop the attacker does not control. This is a cross-tenant identity binding failure: the gem provides no cryptographic guarantee that the `shop` field it hands to application code corresponds to the shop whose data produced the signed body. This falls under the Critical bucket "cross-tenant access."

### Likelihood Explanation
Exploitation only requires becoming a merchant/tenant of the target app — a standard, unprivileged action for any internet user (installing a public Shopify app) — and capturing one legitimate webhook delivery to that shop (trivial, since the attacker controls the receiving endpoint or can proxy it). No access to `api_secret_key`, access tokens, or any other credential beyond normal app installation is needed. The header-vs-signed-bytes mismatch is deterministic and always reproducible.

### Recommendation
Bind the shop identity to the signed payload instead of trusting the unauthenticated header in isolation:
- Include the `shop-domain` (and ideally `topic`, `webhook_id`) header values as part of the signable string used by `HmacValidator`, or
- Independently verify that `request.shop` corresponds to a shop with an active, previously-established session/installation record known to the app before invoking the handler, and reject/flag mismatches, or
- Document and require host applications to cross-check `WebhookMetadata#shop` against their own installed-shop registry prior to acting on the payload, since the gem's HMAC check only proves "sent using this app's secret," not "sent for this shop."

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com`, which shares the app's `api_secret_key` with all other installs.
2. Shopify sends a legitimate webhook (e.g., `orders/paid`) to the app: raw body `B`, header `x-shopify-hmac-sha256: HMAC(secret, B)`, header `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker intercepts this request at their own endpoint (they control routing/proxy for their own shop's webhook subscription) and captures `B` and the valid HMAC header unchanged.
4. Attacker replays the exact same body `B` and `hmac-sha256` header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `Utils::HmacValidator.validate` succeeds because it only checks `B` against the shared secret (`lib/shopify_api/utils/hmac_validator.rb:12-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
6. `Registry.process` calls the handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)` (`lib/shopify_api/webhooks/registry.rb:188-200`), causing the app to process attacker-controlled webhook content as if it belongs to `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
