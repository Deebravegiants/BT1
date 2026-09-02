### Title
Webhook HMAC validates only the raw body, not the `shop-domain`/`topic` headers, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` authenticates the *body bytes* but never binds the `shop-domain`, `topic`, `api-version`, or `webhook-id` headers to that signature. Any party that has ever received one legitimately-signed webhook (e.g., by installing the app on their own store) can replay that body+HMAC pair while freely rewriting the `shop-domain` and `topic` headers, and `Registry.process` will accept it as authentic for an arbitrary victim shop and arbitrary registered topic — including the mandatory GDPR topics (`shop/redact`, `customers/redact`, `customers/data_request`).

### Finding Description
`Request#hmac` and `Request#to_signable_string` are used by `HmacValidator.validate`: [1](#0-0) 

`to_signable_string` returns `@raw_body` alone — none of `shop`, `topic`, `api_version`, or `webhook_id` (all parsed straight from unauthenticated headers) are included in the signable string: [2](#0-1) 

`HmacValidator.validate` computes the HMAC purely over that signable string and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` treats a validated request's headers as trustworthy once the body HMAC passes, and dispatches the handler using the header-derived `shop` and `topic` without any additional binding check: [4](#0-3) 

This breaks the intended identity binding: `hmac == HMAC(secret, body)` is verified, but the equality that actually matters to the host application — `request.shop == the shop that produced this signed body` and `request.topic == the topic that produced this signed body` — is never checked. Contrast this with the OAuth callback path, where `AuthQuery#to_signable_string` explicitly folds `shop`, `host`, `code`, `state`, and `timestamp` into the signed payload: [5](#0-4) 

The webhook path has no equivalent binding, so headers are a completely unauthenticated side-channel next to an authenticated body.

### Impact Explanation
An attacker who controls (or has installed the app on) any single shop can obtain one arbitrarily-topic'd, validly-signed webhook body (any topic, any content) from Shopify for their own store. They can then POST that identical `raw_body` + `hmac-sha256` value to the app's public webhook endpoint while substituting:
- `shop-domain` → a victim shop's domain
- `topic` → any topic the app has registered a handler for, including the mandatory `shop/redact`, `customers/redact`, `customers/data_request` topics

`HmacValidator.validate` still returns `true` because it only checks the body bytes, and `Registry.process` invokes the corresponding handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`, causing the host application to execute shop-scoped/destructive logic (e.g., GDPR redaction, cache invalidation, order/customer processing) under the identity of a shop the attacker does not control. This is a cross-tenant action performed without any credential for the victim shop, satisfying the "cross-tenant access" high/critical impact bar.

### Likelihood Explanation
Likelihood is high for any app that (a) allows public/self-serve installation, which lets an attacker legitimately acquire at least one signed webhook body/HMAC pair for their own store, and (b) registers handlers for the mandatory redact/data-request topics, which virtually every public Shopify app must do to pass App Store review. No access token, `client_secret`, or privileged account is required — only a normal, unprivileged install of the app by the attacker on their own store.

### Recommendation
Bind the header fields to the HMAC computation the same way `AuthQuery` does for OAuth: include `shop`, `topic`, `api_version`, and `webhook_id` (or at minimum `shop` and `topic`) in `to_signable_string`, or otherwise cross-check the parsed body's shop/topic identifiers against the header values before dispatching to a handler. At minimum, document and enforce that host applications must independently verify `request.shop` against the session/tenant context before acting, since the gem's own HMAC check does not provide that guarantee today.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and lets it register for the mandatory topic `customers/redact` (required for Shopify app approval).
2. Shopify sends a legitimately signed webhook to the app:
   - headers: `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: customers/redact`, `x-shopify-hmac-sha256: <valid HMAC over body>`
   - body: `{"shop_id":123,"customer":{...}}`
3. Attacker captures `raw_body` and the `hmac-sha256` value.
4. Attacker POSTs to the same public webhook endpoint with the identical `raw_body`/`hmac-sha256`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses the forged headers; `Utils::HmacValidator.validate(request)` returns `true` because it only re-hashes `raw_body`, per `lib/shopify_api/webhooks/request.rb:36-38` and `lib/shopify_api/utils/hmac_validator.rb:27-31`.
6. `Registry.process` invokes the `customers/redact` handler with `WebhookMetadata.new(shop: "victim.myshopify.com", topic: "customers/redact", body: <attacker-controlled JSON>, ...)`, per `lib/shopify_api/webhooks/registry.rb:188-200`, causing the host app to perform redaction/erasure logic scoped to `victim.myshopify.com` on the attacker's behalf.

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
