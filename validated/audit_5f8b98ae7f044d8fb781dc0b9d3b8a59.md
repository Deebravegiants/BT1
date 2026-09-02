This confirms the finding. The `Webhooks::Request#to_signable_string` returns only `@raw_body`, while `shop` (the tenant-identifying field passed to the handler as `WebhookMetadata.shop`) comes from the `x-shopify-shop-domain` header, which is entirely outside the HMAC-signed bytes.### Title
Webhook shop-domain identity is not covered by HMAC, allowing cross-tenant shop spoofing on any validly-signed webhook - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate(request)` verifies nothing but the JSON body against the app's `api_secret_key`. The `shop` field, which is used downstream as the tenant identity passed to `WebhookHandler#handle` via `WebhookMetadata.shop`, is read from the `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header and is never included in the HMAC-signed bytes. Any party who can obtain one validly-signed webhook body (e.g., a legitimate merchant who has the app installed, receiving their own genuine webhooks) can replay that exact body with the `shop-domain` header changed to any other shop, and the HMAC check will still pass, causing the host application to process the event under a different tenant's identity.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) 

```
def hmac
  Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
end
...
def shop
  T.cast(shopify_header("shop-domain"), String)
end
...
def to_signable_string
  @raw_body
end
```

`Utils::HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest(sha256, api_secret_key, verifiable_query.to_signable_string)` and compares it to `verifiable_query.hmac` using `OpenSSL.secure_compare`: [2](#0-1) 

Because `to_signable_string` is `@raw_body` alone, the `shop` header is completely outside the signed bytes. `Registry.process` only checks the body/HMAC and then hands `request.shop` straight through as the tenant key: [3](#0-2) 

```
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
```

`WebhookMetadata.shop` is a `T::Struct` field that host applications rely on to know which merchant/tenant the event belongs to: [4](#0-3) 

**Binding broken (equality that should hold but doesn't):**
`shop authenticated by HMAC` ≠ `shop delivered to the handler as tenant key`

The bytes verified by the HMAC (`@raw_body` only) do not equal the bytes the identity decision is based on (the `shop-domain` header value). This is exactly the "bytes verified versus bytes parsed" / "shop authenticated versus session key" identity-binding break called out in the report's bug class, reachable entirely inside this gem's `Webhooks::Request` / `HmacValidator` / `Registry.process` code path — no host-application misuse is required, since the gem itself never authenticates the `shop` field.

### Impact Explanation
This is a cross-tenant confusion vulnerability: any actor who can capture (or is a legitimate recipient of, e.g. as an installer of a multi-tenant app) one valid, correctly-HMAC-signed webhook payload can resend it with an arbitrary `shop-domain` header to the app's webhook endpoint. Since `HmacValidator.validate` never inspects the shop header, the forged request is accepted as authentic and dispatched to the handler labeled with the attacker-chosen shop. Depending on what the host app does with `WebhookMetadata.shop` (e.g., looking up/mutating that shop's stored session, access token, or data), this can lead to cross-tenant data corruption or actions being taken against a victim shop's record using an attacker-controlled body — satisfying the "cross-tenant access" criterion for Critical impact.

### Likelihood Explanation
Exploitation requires only replaying HTTP request bytes with one header value changed; no secrets, no TLS interception, and no privileged account are needed beyond obtaining one legitimately-signed webhook body (trivially available to any merchant who installs the app, since Shopify sends them real, signed webhooks for their own shop). The HMAC bytes and comparison logic are entirely internal to the gem, so no host-app misconfiguration is required for the bypass itself.

### Recommendation
- **Short term**: Include the `shop` (and other identity-relevant headers such as topic and API version) in the HMAC-signable string, or otherwise cryptographically bind the `shop-domain` header to the signed body so a replay against a different shop fails verification.
- **Long term**: Treat any field used for tenant/session identity resolution (`shop`, `topic`, `webhook_id`) as untrusted unless it is provably covered by the same HMAC/signature check used to authenticate the request; document clearly in `Utils::VerifiableQuery` that only `to_signable_string`'s content is authenticated, so implementers do not trust unauthenticated attributes exposed alongside it.

### Proof of Concept
1. App receives a genuine webhook from Shopify for `shop-a.myshopify.com` with body `{}` and a valid `x-shopify-hmac-sha256` computed over `{}` with the app's `api_secret_key` (attacker is the legitimate merchant of shop-a and can capture this raw HTTP request).
2. Attacker resends the identical request to the app's webhook endpoint, changing only the `x-shopify-shop-domain` header to `shop-victim.myshopify.com`, leaving body and HMAC header untouched.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`"{}"`) — identical to what was signed originally — and it matches, so validation passes.
4. `handler.handle(data: WebhookMetadata.new(..., shop: "shop-victim.myshopify.com", ...))` is invoked, and the host app processes the (attacker-supplied) body as if it were an authentic event from `shop-victim.myshopify.com`.

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
