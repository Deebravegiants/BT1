This confirms a strong analog to the report's bug class: an identity-binding field (`shop-domain`) is used by the application (`Registry.process` passes `request.shop` to the handler as the tenant identifier) while the HMAC signature that authenticates the webhook covers only the raw body, not the shop header.

### Title
Webhook `shop-domain` header is trusted as tenant identity but is not covered by the HMAC signature - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` authenticates nothing but the JSON body. The `shop-domain` header, which `Registry.process` treats as the trusted tenant/shop identifier passed into every webhook handler, is completely outside the signed content.

### Finding Description
`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which calls `request.to_signable_string` for the signed bytes: [1](#0-0) [2](#0-1) 

`Request#to_signable_string` returns only `@raw_body`, while `Request#shop` is read from the `shop-domain` header and is never part of the signable string: [3](#0-2) 

The resulting `request.shop` is then passed unverified into `WebhookMetadata`, which downstream handlers use as the tenant identity for the webhook event: [4](#0-3) 

This is the exact "field acted on but not covered by the HMAC" pattern named in the rules: the boundary that should hold is `shop-domain header used as tenant identity == shop-domain header covered by the HMAC`, but the gem breaks this equality — the header is used for tenant identity while the HMAC only covers the body. By contrast, the OAuth callback path deliberately signs `shop` as part of its query string in `AuthQuery#to_signable_string`, confirming that the maintainers intended sensitive identity fields to be part of the signable content elsewhere in this same gem: [5](#0-4) 

Because the webhook HMAC secret (`api_secret_key`) is shared across every shop that installs the app (it is the app's `client_secret`, not a per-shop value), any unprivileged attacker who installs the app on their own shop can receive a legitimately-signed webhook (valid `raw_body` + valid `hmac`) for their own store. They can then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `shop-domain` (and `topic`/`webhook-id`) headers to name a victim shop. `Utils::HmacValidator.validate` still passes because it only checks the body against the HMAC, and `Registry.process` forwards `request.shop` (the attacker-controlled, victim's domain) to the handler unauthenticated.

### Impact Explanation
This crosses a tenant boundary purely through this gem's own logic: an app relying on `WebhookMetadata#shop` (as passed by `ShopifyAPI::Webhooks::Registry.process`) to select which merchant's session/data to act on can be made to process attacker-supplied data under a victim shop's identity — a cross-tenant confused-deputy condition using only the gem's documented API, matching the High-severity "cross-tenant access" category in the rules.

### Likelihood Explanation
Any developer can register as a Shopify Partner and install their own app instance (or use a shared/public app) to obtain a validly-signed webhook body+HMAC pair signed with the app's real `client_secret`, since the same secret signs webhooks for all shops using that app. No access to the victim's credentials, token, or `client_secret` is required — only network access to the app's public webhook endpoint and knowledge of the victim's `myshopify.com` domain (which is not secret).

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) header values inside the bytes covered by the HMAC verification, e.g. by having `Request#to_signable_string` combine the shop domain with the raw body (matching Shopify's documented practice of scoping tenant identity into the verified payload), or by requiring hosts to independently bind `request.shop` to the recipient endpoint/session before trusting it as tenant identity.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`; Shopify sends a webhook to the app's endpoint with `x-shopify-shop-domain: attacker.myshopify.com`, a JSON body, and a valid `x-shopify-hmac-sha256` computed with the app's `client_secret` over the body only.
2. Attacker captures `raw_body` and the valid `hmac` header value.
3. Attacker replays a POST to the same endpoint with the identical `raw_body`/`hmac`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` (via `Request#to_signable_string` returning only `@raw_body`) succeeds because the signature only ever covered the body.
5. `Registry.process` forwards `WebhookMetadata.new(..., shop: "victim.myshopify.com", ...)` to the app's handler, which acts on the victim's tenant using attacker-controlled data.

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
