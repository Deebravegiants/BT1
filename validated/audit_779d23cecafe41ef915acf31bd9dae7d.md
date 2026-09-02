### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates its HMAC over the raw request body only. The `shop-domain` header — which the registry uses as the authoritative tenant identifier when invoking the merchant's webhook handler — is never included in the signed material. Any attacker capable of producing (or replaying) one validly-signed webhook body for the shared app secret can attach an arbitrary `shop-domain` header and have `Registry.process` deliver that body to the handler under a different shop's identity.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the (unsigned) `shopify-shop-domain`/`x-shopify-shop-domain` header: [2](#0-1) 

`HmacValidator.validate` verifies the HMAC purely against `to_signable_string`, i.e. the body, never the headers: [3](#0-2) 

`Registry.process` trusts `request.shop` as the tenant identity and forwards it, unchecked against the HMAC, straight into the `WebhookMetadata` passed to the app's handler: [4](#0-3) [5](#0-4) 

This breaks the identity binding the host application relies on: `HMAC-verified bytes == the bytes used to determine which shop/tenant the payload belongs to`. In practice, `shop` is not part of the signed payload, so:

`HMAC(raw_body, client_secret)` is valid regardless of the `shop-domain` header value.

Contrast this with the OAuth callback path, `Auth::Oauth::AuthQuery`, where `shop` **is** explicitly part of the signed string: [6](#0-5) 

So the OAuth flow correctly binds `shop` to the signature, but the webhook flow does not — an inconsistent security boundary within the same gem.

### Impact Explanation
Shopify webhooks for a given app all share the same `client_secret` HMAC key across every installed shop (this gem intentionally supports rotating/old secrets globally, not per-shop, per `Context.api_secret_key` / `Context.old_api_secret_key`). Because the `shop-domain` header is excluded from the signed content, an attacker who controls (or has installed the app on) one shop can capture a legitimately-signed webhook body/HMAC pair from their own tenant and replay it to the app's public webhook endpoint with the `shop-domain` header rewritten to a victim shop. `Registry.process` will pass HMAC validation and invoke the app's handler with `WebhookMetadata#shop` set to the victim's domain while the body content is attacker-controlled. Any host application that uses `data.shop` as the tenant key to write, delete, or reconcile data (a documented and expected usage pattern of this struct) will perform a cross-tenant write/action against the victim's records using attacker-supplied content. This satisfies the "cross-tenant access" Critical-impact category defined in scope.

### Likelihood Explanation
Exploitation only requires: (1) the attacker be able to install/operate the target app on at least one shop they control (a normal, unprivileged capability for any Shopify merchant/developer), and (2) the ability to send an arbitrary HTTP request to the app's public webhook endpoint with a custom header — both trivially available to an unprivileged internet user. No access token, `client_secret`, or victim credentials are needed.

### Recommendation
Include the shop identity in the signed/verified material for webhooks, or otherwise bind it to a value provable to belong to the shop that produced the HMAC-signed body — e.g., verify that the `shop-domain` header matches a shop already known to have installed the app for that specific webhook subscription/topic, or require Shopify's webhook subscription ID (bound at registration time) rather than trusting the raw header value as the tenant identifier. At minimum, document that `WebhookMetadata#shop` is unauthenticated and must not be used as a sole tenant key without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers any webhook (e.g. `orders/create`), receiving a real request with headers:
   - `x-shopify-hmac-sha256: <valid HMAC of raw_body signed with the app's shared client_secret>`
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - raw body `B`
2. Attacker replays this exact `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but changes the header to `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only recomputes HMAC over `raw_body` (`Request#to_signable_string`), which is unchanged: [1](#0-0) 
4. `ShopifyAPI::Webhooks::Registry.process` calls `handler.handle` with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`, even though body `B` was produced by/for the attacker's own shop: [7](#0-6) 
5. Any handler implementation that keys tenant data off `data.shop` now processes attacker-controlled content under the victim's tenant identity.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
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
