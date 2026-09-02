## Analysis

The webhook processing path in `ShopifyAPI::Webhooks::Registry.process` validates only the HMAC over the request body, but attributes the webhook to a shop taken from an unauthenticated header. This mirrors the reported bug class: a value that is *acted upon* (tenant identity) is not covered by the integrity check that is supposed to authenticate the request. [1](#0-0) 

`Request#hmac` and `Request#to_signable_string` only ever operate on `@raw_body`; `shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the HMAC. [2](#0-1) 

`Registry.process` validates `Utils::HmacValidator.validate(request)` (body-only) and then immediately builds `WebhookMetadata` using `request.shop`, which was never part of the signed material, and hands it to the app's handler as the trusted tenant identifier.

Contrast with the OAuth callback path, where `shop` **is** included in the signable string, so the HMAC genuinely binds shop identity there: [3](#0-2) 

### Title
Cross-tenant webhook spoofing via unauthenticated `shop-domain` header not covered by HMAC - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#hmac` validates only the raw request body against the app's `api_secret_key`. The `shop` (and `topic`, `webhook_id`) values are read from HTTP headers that are never part of the signed payload. `ShopifyAPI::Webhooks::Registry.process` treats a successful HMAC check as proof of the entire request's authenticity, including `request.shop`, and passes that unverified shop value straight to the app's `WebhookHandler` as the tenant identity.

### Finding Description
The identity binding that should hold is:
`shop value trusted by the handler == shop value covered by the HMAC signature`

In this gem that equality does not hold:
- `hmac` is computed as `HMAC-SHA256(secret, raw_body)` — see `to_signable_string` returning only `@raw_body`.
- `shop` is taken from `shopify-shop-domain`/`x-shopify-shop-domain`, a plain HTTP header with no relation to the HMAC input.
- `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) only calls `Utils::HmacValidator.validate(request)`, which recomputes the digest over the body and compares it to the `hmac-sha256` header — it never checks that `shop` was part of what was signed.

Because the HMAC is body-only, any body+hmac pair that is valid for *one* shop is also valid for *any other shop*, since the signature makes no reference to which shop it belongs to. An attacker who can obtain one legitimate `(raw_body, hmac)` pair — trivially available to them, e.g. by installing the app on their own development/free shop and receiving a real webhook — can resend that exact body and HMAC to the app's public webhook endpoint while substituting an arbitrary victim shop domain in the `x-shopify-shop-domain` header. `HmacValidator.validate` still succeeds (it never looked at the shop header), and `Registry.process` dispatches the handler with `data.shop` set to the attacker-chosen victim domain.

### Impact Explanation
This breaks the tenant boundary the whole gem exists to protect. Any downstream app logic that uses `data.shop` from `WebhookMetadata` to select which merchant's records to update, invalidate, or act on can be tricked into applying attacker-supplied webhook bodies to a different tenant's data — a cross-tenant access primitive achieved without any credential belonging to the victim shop.

### Likelihood Explanation
High. The prerequisite is only the ability to obtain any one valid `(body, hmac)` pair for the target app, which is achievable trivially by installing the app on an attacker-controlled shop (a normal, unprivileged action) and capturing/replaying its own real webhook deliveries with a forged `shop-domain` header value pointed at any other shop name. No secrets, tokens, or victim cooperation are required.

### Recommendation
Bind the shop (and topic/webhook id, as relevant) into the material that is authenticated, or otherwise verify that the claimed shop is one the app actually expects/has an active session for, and treat the header purely as untrusted routing metadata until independently corroborated (e.g., cross-checked against a known/installed shop record) rather than passed on as ground truth in `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com`, triggering a legitimate webhook delivery with body `B` and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC(secret, B)`).
2. Attacker sends a POST to the app's webhook endpoint with the same body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H`.
4. The handler is invoked with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though the payload never originated from Shopify for that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
