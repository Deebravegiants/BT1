This confirms the key asymmetry: `AuthQuery#to_signable_string` (OAuth callback) binds `shop` into the HMAC-signed string, but `Request#to_signable_string` (webhook) does not — it signs only `@raw_body`, while `shop`, `topic`, and `webhook_id` come from unauthenticated HTTP headers and are trusted as-is once the body's HMAC checks out.

### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , while `shop`, `topic`, and `webhook_id` are read straight from HTTP headers without being part of the signed payload [2](#0-1) . `Utils::HmacValidator.validate` only checks that the raw body matches the HMAC, and never binds the `shop` field to that signature [3](#0-2) . `Registry.process` trusts `request.shop` and forwards it verbatim to the app's `WebhookHandler` as the tenant identifier once the body HMAC passes [4](#0-3) .

### Finding Description
The equality the HMAC is supposed to guarantee is: `hmac == HMAC(client_secret, signed_content)` where `signed_content` should bind everything the handler acts on — topic, shop, and body. Instead, `signed_content == raw_body` only [5](#0-4) . By contrast, the OAuth callback path explicitly includes `shop` in its signable string, showing that binding the shop identifier into the signature is the intended pattern elsewhere in this gem [6](#0-5) .

Because `shop-domain` (and `topic`/`webhook-id`) are excluded from the signed content, any party who can obtain one valid `(raw_body, hmac)` pair for the shared app `client_secret` — e.g., a merchant who installed the app and received a legitimate webhook to their own shop — can replay that exact `raw_body`/`hmac` pair while substituting an arbitrary `shopify-shop-domain` header value. `HmacValidator.validate` will still return `true` because it only recomputes the HMAC over `raw_body` [7](#0-6) , and `Registry.process` will pass the forged `shop` straight into `WebhookMetadata` for the handler to act on [8](#0-7) .

### Impact Explanation
This breaks the tenant-authentication equality: `shop authenticated by the HMAC` != `shop the handler trusts for its business logic`. A host application (built per this gem's documented `WebhookHandler` interface) that keys per-tenant data/actions off `WebhookMetadata#shop` — the intended and documented usage — can be tricked into attributing a replayed webhook payload to a shop that never sent it, i.e. cross-tenant access/attribution using a signature that was never computed over that shop's identity.

### Likelihood Explanation
Exploitation only requires possession of one legitimately HMAC-signed webhook body (obtainable by any merchant who installs the app, since all shops share the same app `client_secret`), plus the ability to send an HTTP request to the app's webhook endpoint with a forged `shopify-shop-domain` header — no access to `client_secret`, tokens, or TLS interception is required.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable string used by `Request#to_signable_string`, mirroring the approach already used in `Oauth::AuthQuery#to_signable_string` [6](#0-5) , so the HMAC binds the full identity context the handler will act on, not just the body bytes.

### Proof of Concept
1. App installs on shop `victim.myshopify.com`; attacker's own shop `attacker.myshopify.com` also has the app installed and receives a legitimate webhook with body `{"id":1}` and header `x-shopify-hmac-sha256: <valid_hmac_of_body>`.
2. Attacker replays the identical `raw_body` and `hmac` value to the app's webhook endpoint, but sets header `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `raw_body` only and succeeds [9](#0-8) .
4. `WebhookMetadata.new(shop: request.shop, ...)` is built with `shop == "victim.myshopify.com"` [8](#0-7) , and the handler executes business logic believing the payload originated from `victim.myshopify.com`, despite the signature never having covered that value.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
