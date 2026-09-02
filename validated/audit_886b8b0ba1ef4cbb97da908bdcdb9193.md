### Title
Webhook shop-domain, topic, and webhook-id headers are unauthenticated by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, and `webhook_id` from raw HTTP headers, but `to_signable_string` only returns the raw request body. `Utils::HmacValidator.validate` verifies the HMAC solely against that body, so the shop/topic identity fields used downstream to dispatch and attribute the webhook are never bound to the signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#hmac` reads the `hmac-sha256` header, and `#to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

The `shop`, `topic`, and `webhook_id` fields are pulled straight from unauthenticated headers, independent of the signed content: [3](#0-2) 

`Utils::HmacValidator.validate` recomputes the HMAC over `verifiable_query.to_signable_string` (the body only) and compares it to `verifiable_query.hmac`: [4](#0-3) 

`Webhooks::Registry.process` trusts this validation, then dispatches using `request.shop` and `request.topic` taken directly from the (unsigned) headers: [5](#0-4) 

This breaks the intended identity binding: `HMAC-verified bytes (raw_body) != identity fields acted on (shop-domain, topic, webhook-id headers)`. Contrast this with `Auth::Oauth::AuthQuery`, where `shop` (and `host`, `code`, `state`, `timestamp`) are explicitly included in `to_signable_string`, so the shop is correctly bound to the signature during OAuth callback validation: [6](#0-5) 

No equivalent binding exists for the webhook `shop`/`topic`/`webhook_id` headers.

### Impact Explanation
Because only the body is signed, any request bearing a previously-observed valid `(raw_body, hmac)` pair (e.g. from a webhook legitimately delivered to the attacker's own store) can be replayed with a different `shopify-shop-domain` header — and the library will still report the HMAC as valid via `HmacValidator.validate`. The consuming application's handler receives `WebhookMetadata`/dispatch data claiming to be from an arbitrary attacker-chosen shop while the signature only vouches for the body bytes. This is a cross-tenant identity confusion: a handler acting on `request.shop` to look up per-tenant sessions, credentials, or state can be tricked into operating on behalf of, or attributing actions to, a different merchant than the one that actually sent the body.

### Likelihood Explanation
Exploitation requires the attacker to control (or observe) at least one genuine signed webhook body for their own shop (trivial — any merchant can install the app and trigger its own webhooks), then replay it to the app's public webhook endpoint with a forged `shop-domain`/`topic` header. No access token, `client_secret`, or privileged account is required beyond what any unprivileged Shopify merchant already has.

### Recommendation
Include the `shop`, `topic`, and `webhook_id` header values in the signable string used for HMAC verification (or otherwise cryptographically bind them, e.g., by having `to_signable_string` concatenate the canonical header values with the body), so that `HmacValidator.validate` fails if any of these identity fields are altered independently of the signed body.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`) with an empty/generic JSON body `{}`.
2. Shopify signs and delivers the webhook: headers include `x-shopify-hmac-sha256: <valid HMAC of "{}">`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`.
3. Attacker resends the identical raw body `"{}"` and identical `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks the HMAC against `request.to_signable_string` (`"{}"`) — this still passes because the body and HMAC pair is genuinely valid. [7](#0-6) 
5. The handler receives `shop: "victim.myshopify.com"` (spoofed) and `topic: "orders/create"`, believing the event legitimately originated from the victim's store, despite the HMAC never having covered that header.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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
