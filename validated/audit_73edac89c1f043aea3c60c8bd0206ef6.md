### Title
Webhook shop-domain identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-signable string from the raw body only. The `shop-domain` header — which the registry uses as the tenant identity for dispatching webhook data to the app's handler — is never included in the signed material. Because the app's `api_secret_key` is shared across all shops installed on the app, any request bearing a validly-signed body can have its `shop-domain` header rewritten to any other shop, and it will still pass HMAC validation.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `shop` is read directly, unauthenticated, from the `x-shopify-shop-domain`/`shopify-shop-domain` header: [2](#0-1) 

`ShopifyAPI::Webhooks::Registry.process` validates the HMAC over that same signable string (body-only) and then builds `WebhookMetadata` — the tenant-identifying payload delivered to the app's handler — directly from the unauthenticated `request.shop` and `request.topic`: [3](#0-2) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string`, i.e. from the body, never from the shop field: [4](#0-3) 

The equality that should hold is: *shop authenticated by the HMAC == shop consumed by the handler as the tenant identity*. In this code path that equality is broken — the shop field consumed by the handler is completely outside the scope of what the HMAC covers. By contrast, the OAuth callback's `AuthQuery#to_signable_string` explicitly folds `shop` into the signed payload, showing the library is capable of, and normally does, bind identity fields into the HMAC: [5](#0-4) 

### Impact Explanation
Because a single `api_secret_key` is shared by the app across every shop that installs it, any user who can obtain one legitimately-signed webhook body/HMAC pair for their own shop (e.g., by installing the app on their own store and triggering an event) can replay that exact body+HMAC to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header for a different, unrelated shop. The signature check passes because the shop header was never part of the signed content, and the app's handler will process the event believing it originated from the spoofed shop. This is a cross-tenant data/identity confusion: an app relying on this library's webhook verification to determine "which shop does this event belong to" cannot trust that value.

### Likelihood Explanation
Any shop that installs the app is, by definition, an "unprivileged internet user" relative to other tenants of the same app. No access token, leaked `client_secret`, or privileged account for the target tenant is required — only a legitimately-obtained signed webhook body from the attacker's own installation, which is trivial to acquire (e.g., trigger any webhook topic in their own store).

### Recommendation
Include the tenant-identifying headers (`shop-domain`, and ideally `topic`/`webhook-id`) in the material that is HMAC-verified, or otherwise cryptographically bind them (e.g., verify the header value against a value embedded/covered by the signature) so that a body signed for one shop cannot be replayed under a different shop's identity.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) to receive a genuine Shopify webhook POST with a valid `x-shopify-hmac-sha256` for the raw body.
2. Capture that raw body and its HMAC.
3. Replay the identical body and HMAC to the app's webhook endpoint, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` succeeds (it only checks the body), and `ShopifyAPI::Webhooks::Registry.process` invokes the app's handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, causing the app to process attacker-controlled data as if it came from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
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
