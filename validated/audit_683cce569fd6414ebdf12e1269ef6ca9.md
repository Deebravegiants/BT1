## Finding: Webhook `shop` (tenant identifier) is not covered by the HMAC signature

### Title
Cross-Tenant Webhook Spoofing via Unsigned `shop-domain` Header - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the shop/tenant identity is taken from an HTTP header that is never included in that signature. `Registry.process` validates the HMAC and then blindly forwards the header-derived `shop` value to the app's webhook handler as the tenant identity, breaking the binding between "bytes verified" and "tenant attributed."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is completely outside the signed data: [2](#0-1) 

`HmacValidator.validate` (via `VerifiableQuery`) only checks `hmac` against `to_signable_string`, i.e. the body bytes — it never binds `shop` to the signature: [3](#0-2) [4](#0-3) 

`Registry.process` performs exactly that check and, once it passes, forwards the unauthenticated `request.shop` value straight into the handler's metadata as the tenant identity for the payload: [5](#0-4) 

The binding that should hold is: `shop` used to attribute/act on the payload == `shop` cryptographically bound to the verified bytes. Here it does not — the equality is `hmac(raw_body) == valid` while `shop` is taken from an arbitrary, unsigned header, so an attacker who possesses one legitimately-signed `(raw_body, hmac)` pair (e.g., captured from a webhook to their own store, or from a store they control) can resend that exact pair while substituting a different `x-shopify-shop-domain` header value. The HMAC still validates because it never covered the header, and `Registry.process` will hand the host application a `WebhookMetadata` claiming the payload belongs to the attacker-chosen shop.

### Impact Explanation
Host applications built on this gem key per-tenant side effects (uninstall cleanup, data deletion for `shop/redact`/`customers/redact`, order/customer ingestion, entitlement updates, etc.) off `WebhookMetadata#shop`. Because this field is not bound to the signature, an attacker can cause the host app to process attacker-controlled but validly-signed body content under a victim shop's identity — a cross-tenant confusion that can lead to unauthorized data mutation/deletion or data being written into the wrong tenant's context. This matches the report's "on-behalf" pattern: the caller-supplied identity (`shop`) is not checked against what was actually authenticated (the HMAC-signed bytes).

### Likelihood Explanation
The attacker needs one previously valid `(raw_body, hmac)` pair, which is obtainable without any secret — e.g., by installing the app on their own store to receive a real signed webhook, or intercepting/replaying one. No `api_secret_key`, access token, or privileged access is required; only network access to the app's public webhook endpoint and one captured legitimate webhook body.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`/`api_version`) in the HMAC-signed material, or independently verify the `shop-domain` header against a value bound to the signed payload/session before trusting it in `WebhookMetadata`. At minimum, document and enforce that `request.shop` must not be treated as authenticated data by downstream handlers unless the transport itself (mTLS, source IP allow-list) additionally guarantees origin.

### Proof of Concept
```ruby
# Attacker captures one legitimate webhook delivered to their own store:
raw_body = '{"id":123,"note":"legit payload from attacker-owned store"}'
valid_hmac = <captured "x-shopify-hmac-sha256" value from that real webhook>

# Attacker replays the exact same body+hmac to the app's webhook endpoint,
# but swaps the shop-domain header to a victim shop:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac,       # still valid: HMAC only covers raw_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled, unsigned
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (body unchanged),
#    handler receives WebhookMetadata(shop: "victim-shop.myshopify.com", body: attacker_payload)
``` [5](#0-4)

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

**File:** lib/shopify_api/utils/verifiable_query.rb (L11-16)
```ruby
      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
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
