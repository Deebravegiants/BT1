I have enough evidence to confirm the finding. Let me finalize the analysis.

### Title
Webhook `shop` identity is trusted from an unauthenticated header while the HMAC only signs the raw body, allowing cross-tenant webhook attribution - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) exclusively from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, while `Utils::HmacValidator` only verifies the HMAC over the raw request body. `Registry.process` then hands this unauthenticated `shop` value straight to the app's webhook handler as trusted tenant metadata. The binding "HMAC-verified bytes == bytes acted upon" is broken because the `shop` field is acted upon but never covered by the signature.

### Finding Description
`Request#hmac` and `Request#to_signable_string` compute/verify the signature over `@raw_body` only: [1](#0-0) 

`Request#shop` is read directly from a header that is never part of the signed content: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identity for the handler, without any cross-check that this shop is the one the signed body actually belongs to: [3](#0-2) 

Because a single app-wide `Context.api_secret_key` is used to validate every shop's webhook HMAC (there is no per-shop secret), any HMAC-body pair captured from one legitimately-signed delivery (e.g., a webhook delivered to the attacker's own installed/trial store) remains a valid signature for that body regardless of which shop the header claims. An attacker who controls one tenant can therefore replay a captured `(raw_body, hmac)` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop's domain. `HmacValidator.validate` passes because it never inspects the `shop` field: [4](#0-3) 

The app's handler then receives `WebhookMetadata` with `shop` set to the victim's domain but a body that was actually generated for the attacker's own shop — a broken equality between "the shop whose secret validated the signature over this body" and "the shop the code believes this body is about." This contrasts with `Auth::Oauth::AuthQuery#to_signable_string`, which explicitly folds `shop` into the signed string so shop cannot be swapped post-signature: [5](#0-4) 

### Impact Explanation
If a host application uses `data.shop` from `WebhookMetadata` (as the gem's own webhook handler API is designed to be used) to select which tenant's records to mutate, an attacker with any legitimate installed shop can forge a webhook event that appears to originate from a completely different, victim merchant, causing cross-tenant data confusion/corruption (e.g., misattributing `orders/*`, `app/uninstalled`, or GDPR redact events to the wrong shop).

### Likelihood Explanation
Exploitation only requires the attacker to install the app on a shop they control (a normal, low-privilege action for any Shopify merchant/developer), observe one legitimate webhook delivery's raw body and HMAC header, and replay it with a modified shop-domain header — no `api_secret_key`, access token, or privileged account is required.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and lets Shopify deliver a legitimate webhook (e.g., `orders/create`) to the app's webhook endpoint. They capture the raw POST body `B` and the `x-shopify-hmac-sha256` header `H`.
2. Attacker replays a new POST to the same endpoint with body `B`, header `x-shopify-hmac-sha256: H` unchanged, but `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed; `HmacValidator.validate(request)` recomputes the HMAC over `B` with the app's single `api_secret_key` and it matches `H`, so validation succeeds (`lib/shopify_api/utils/hmac_validator.rb`).
4. `Registry.process` calls the handler with `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: JSON.parse(B), ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), even though `B` was never signed for, nor originated from, `victim.myshopify.com`.

### Recommendation
Bind the shop identity into the verified signature surface: include the `shop-domain` header value in `Request#to_signable_string` (or otherwise cryptographically bind it), and/or require callers of `Registry.process` to supply the expected shop and assert `request.shop == expected_shop` before invoking the handler, so a captured `(body, hmac)` pair from one tenant cannot be re-attributed to another tenant merely by swapping a header.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
