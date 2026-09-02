### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC of the raw request body, but the `shop` value used to attribute the webhook to a tenant is read from an HTTP header that is never included in the signed bytes. This breaks the binding `shop authenticated == shop the payload is attributed to`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is instead extracted from the `shopify-shop-domain`/`x-shopify-shop-domain` header and is completely independent of the signed content: [2](#0-1) 

`Registry.process` verifies the request using `Utils::HmacValidator.validate(request)`, which only compares the HMAC over `to_signable_string` (i.e., the body): [3](#0-2) [4](#0-3) 

Once the HMAC check passes, `request.shop` (the unauthenticated header value) is handed to the app's handler as the tenant identity in `WebhookMetadata`: [5](#0-4) 

Because the signature only binds the body bytes and never binds the `shop-domain` header, any party that obtains one legitimately-signed webhook body/HMAC pair (e.g., by receiving a real webhook for their own installed shop) can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header. `Utils::HmacValidator.validate` still passes because the signature was computed only over the body, and the handler will process the payload under the attacker-chosen shop identity. This is exactly the pattern called out in the rules: "a shop authenticated versus the shop stored as a session key" / "bytes verified versus bytes parsed."

Contrast this with the OAuth callback path, where `shop` **is** included in the HMAC-signed payload: [6](#0-5) 
This confirms the library elsewhere correctly binds `shop` into the signature — the webhook path is the outlier that omits it.

### Impact Explanation
An attacker who can obtain any one valid (body, HMAC) pair — trivially available to any user who installs the app on their own store and receives a webhook — can forge webhooks that the host application will process as if they originated from a different, victim shop. Depending on how the host app's webhook handlers use `WebhookMetadata#shop` (e.g., to look up/update tenant records, credentials, or state), this enables cross-tenant data injection/corruption without any access to the victim's credentials or the app's `client_secret`. This matches the in-scope "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any attacker capable of installing the app on a shop they control (a normal, unprivileged flow) — they can capture a real webhook body+signature and replay it with a spoofed `shop-domain` header to the same public webhook endpoint. No secret, token, or privileged access is required.

### Recommendation
Include the shop identity (and any other fields the handler relies on for tenant attribution) inside the HMAC-signed material, or otherwise cryptographically bind the `shop-domain` header to the signed body (e.g., signing `shop + raw_body` instead of `raw_body` alone), and reject the request if these do not match. At minimum, document that `request.shop` must never be trusted for authorization decisions without additional verification (e.g., cross-checking against a known/stored session for that shop) in `lib/shopify_api/webhooks/registry.rb`.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a legitimate webhook: body `B`, headers include `x-shopify-hmac-sha256: HMAC(secret, B)` and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker replays the exact same body `B` and HMAC header to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes HMAC over `raw_body` — the check passes because `B` and its HMAC are unchanged. [7](#0-6) 
4. The handler is invoked with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop == "victim.myshopify.com"`, even though the payload was never actually generated for that shop. [2](#0-1)

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
