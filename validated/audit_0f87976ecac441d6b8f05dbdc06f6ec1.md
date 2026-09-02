### Title
Webhook `shop-domain` header is trusted for handler dispatch while only the raw body is HMAC-covered - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` from HTTP headers, but `to_signable_string` — the value actually fed into the HMAC check — is only the raw request body. `Registry.process` validates the HMAC and then hands `request.shop`/`request.topic` straight to the app's handler as trusted identity data, even though those header values are never bound to the signature.

### Finding Description
`Webhooks::Request#to_signable_string` returns just `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are pulled directly from headers, none of which participate in the signable string: [2](#0-1) 

`Registry.process` validates the HMAC over that signable string (body only) and then immediately trusts `request.shop`/`request.topic` to build `WebhookMetadata` passed to the registered handler: [3](#0-2) 

`HmacValidator.validate` only compares `computed_signature` (over `to_signable_string`) against the received `hmac`; it never incorporates the headers: [4](#0-3) 

This is the same bug class as the reported `Governance::_execute` ordering flaw: an identity-relevant field (`shop`) is *acted upon* by privileged logic (dispatch to the app's webhook handler, which typically uses `shop` to select the tenant/session to operate on) while the binding that is supposed to authenticate that field (the HMAC) never actually covers it. The equality that should hold — `shop-header == shop-that-produced-the-signed-bytes` — is not enforced anywhere in this gem.

Because the HMAC secret (`Context.api_secret_key`, the app's `client_secret`) is shared across all shops installed on a given app, any shop that has legitimately installed the app can obtain a valid `(raw_body, hmac)` pair for a webhook (e.g. by triggering an event in its own store and capturing the delivery, or simply by controlling its own webhook receiver first). It can then replay that exact `(raw_body, hmac)` pair to the app's public webhook endpoint while substituting an arbitrary victim `shop-domain` header. `HmacValidator.validate` still succeeds because it never inspects the header, and `Registry.process` forwards the forged `shop` value to the handler as if it were authenticated.

### Impact Explanation
This crosses a tenant boundary inside the library's own trusted-data contract: the gem asserts to the app author, via `WebhookMetadata#shop`, that the payload was HMAC-verified and thus safe to attribute to that shop. Any app that keys per-tenant behavior (activating a session for that shop, writing to that shop's data store, billing decisions, uninstall/redact handling, etc.) purely off the value provided by this library can be made to act on attacker-chosen body content under a victim shop's identity — a cross-tenant confusion that fits the Critical "cross-tenant access" bucket for apps that rely on this metadata as authenticated.

### Likelihood Explanation
Likelihood is constrained by two facts: (1) the attacker must already be an app-installing party (control at least one shop that has the app installed) to obtain a genuine `(body, hmac)` pair, and (2) the resulting impact depends on the host app trusting `WebhookMetadata#shop` without independently re-validating it against Shopify's own webhook delivery guarantees (Shopify normally only sends the real header alongside the real body over its own infrastructure, so the *practical* exploit requires an attacker hitting the app's public webhook endpoint directly rather than going through Shopify). Within this gem alone, nothing prevents header spoofing once a valid signed body/hmac pair for any shop is known, so the vulnerable code path is concretely present and unconditionally reachable via `Registry.process`.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header values into the HMAC-signed content, or otherwise cryptographically authenticate them, before trusting them in `WebhookMetadata`. At minimum, `Request#to_signable_string` should incorporate the `shop-domain` header so that `HmacValidator.validate` fails if the header is altered relative to what Shopify actually signed, mirroring the recommended fix pattern of checking the identity-binding condition before/at the point the value is trusted rather than after acting on it.

### Proof of Concept
```ruby
# Attacker controls "attacker-shop.myshopify.com" and has it installed on the target app.
# Step 1: capture a legitimate webhook delivery for attacker-shop.
raw_body    = '{"id":123,"note":"malicious payload"}'
valid_hmac  = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), Context.api_secret_key, raw_body)

# Step 2: replay the exact (body, hmac) pair against the app's public webhook endpoint,
# but swap the shop-domain header for the victim shop.
forged_headers = {
  "shopify-topic"       => "orders/create",
  "shopify-hmac-sha256" => Base64.encode64(valid_hmac),
  "shopify-shop-domain" => "victim-shop.myshopify.com", # not covered by hmac
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (body/hmac match),
#    handler.handle(data: WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...))
#    is invoked with attacker-controlled body attributed to the victim shop.
```

### Citations

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
