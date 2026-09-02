### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing tenant-identity spoofing in `ShopifyAPI::Webhooks::Registry.process` - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw request body only, while the `shop` (tenant identity) is read from a separate, unauthenticated HTTP header. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC over the body and then hands the *unverified* `shop` value straight to the app's webhook handler as the tenant identifier. The binding the protocol needs — `shop == the shop that Shopify computed the HMAC for` — is never actually checked; only `hmac == HMAC(body, secret)` is checked.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are: [1](#0-0) [2](#0-1) 

`to_signable_string` returns only `@raw_body`; `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from HTTP headers and are excluded from the signable string entirely.

`HmacValidator.validate` (shared by both webhook and OAuth callback verification) only checks that `hmac` matches `HMAC-SHA256(to_signable_string, api_secret_key)`: [3](#0-2) 

`Registry.process` performs exactly this check and then trusts `request.shop` unconditionally to build the tenant-scoped payload delivered to the app's handler: [4](#0-3) 

Because `shop-domain` is not part of the signed material, the equality the library implicitly claims to enforce — `authenticated_shop == request.shop` — does not hold. Any two values are accepted as long as the *body* HMAC matches; the shop header can be swapped for a different value without invalidating the signature. Contrast this with `Auth::Oauth::AuthQuery#to_signable_string`, where `shop` **is** included in the signed parameters and thus is properly bound to the HMAC: [5](#0-4) 

This asymmetry shows the webhook path is the outlier: the OAuth callback correctly binds `shop` into the signature, but the webhook `Request` does not.

### Impact Explanation
Any consumer of this gem that follows the documented pattern — calling `Registry.process(request)` and using `WebhookMetadata#shop` (built directly from the unauthenticated header) to look up per-tenant state, credentials, or to route processing — is exposed to cross-tenant data confusion. An attacker who can deliver *any* one webhook body with a valid HMAC (e.g. a webhook naturally generated for their own store, whose HMAC is computed by Shopify with the app's real `client_secret` over that body) can resend the same body/HMAC pair to the app's endpoint while substituting the `shopify-shop-domain` / `x-shopify-shop-domain` header with an arbitrary shop domain. `Registry.process` will still validate successfully (only the body is checked) and will hand the handler a `WebhookMetadata` claiming to be from the attacker-chosen shop, while the payload content actually belongs to the attacker's own store. This breaks the identity binding required for safe multi-tenant webhook processing and can lead to cross-tenant data being attributed to, or acted upon under, a victim shop's identity within the app.

### Likelihood Explanation
Exploitation requires only unauthenticated network access to the app's webhook endpoint plus one legitimately-signed body (trivially obtainable by any user who can install the app on their own store, since Shopify signs every real webhook payload with the app's shared secret). No leaked credentials, TLS interception, or privileged access is needed — only the ability to POST to the public webhook URL, which is inherently unauthenticated and internet-reachable. This is squarely an unprivileged-internet-user analog to the reported "sandwich" bug-class: exploiting a value that is *acted upon* (here, tenant identity) but not *covered by the cryptographic binding* (here, the HMAC).

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the HMAC-signable string for webhook requests, or otherwise cryptographically bind the shop header to the signed body (e.g., require the app to independently verify that the `shop-domain` header matches a shop known to have this webhook subscription/topic registered before trusting it). At minimum, document prominently that `WebhookMetadata#shop` is not covered by the HMAC and must not be trusted for tenant lookups without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`). Shopify sends a POST to the app's webhook endpoint with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of body>`, and the JSON body.
2. Attacker replays the exact same raw body and HMAC header, but rewrites `x-shopify-shop-domain` to `victim.myshopify.com`.
3. The app calls `ShopifyAPI::Webhooks::Registry.process(request)`, which invokes `Utils::HmacValidator.validate(request)`; since validation only hashes `@raw_body`, it succeeds unchanged.
4. `handler.handle(data: WebhookMetadata.new(topic:, shop: request.shop, ...))` is invoked with `shop == "victim.myshopify.com"`, even though the body content is attacker-controlled data from `attacker.myshopify.com`. Any app logic keyed on `data.shop` (e.g., "store this order data under shop X") is fooled into attributing/act­ing on attacker data as if it belonged to `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
