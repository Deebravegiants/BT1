### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by verifying an HMAC over the raw request body [1](#0-0) . The HMAC signable string is defined as just `@raw_body` [2](#0-1) , while the `shop` (tenant identity), `topic`, `api_version`, and `webhook_id` values are all read from unauthenticated HTTP headers that are never part of the signed payload [3](#0-2) . This is the same class of defect as the report's core issue: a field that downstream logic relies on for a security decision (the "active" state / tenant identity) is not actually bound by the mechanism supposed to guarantee its integrity (the `ActiveProposals` array vs. the HMAC signature).

### Finding Description
`Utils::HmacValidator.validate` computes an HMAC over `verifiable_query.to_signable_string` and compares it against the `hmac` field via `OpenSSL.secure_compare` [4](#0-3) . For `Webhooks::Request`, `to_signable_string` returns only the raw body, and `hmac` is decoded from the `X-Shopify-Hmac-Sha256` header [5](#0-4) [2](#0-1) . The equality the gem is implicitly asserting is:

`HMAC(app_secret, raw_body) == received_hmac` ⇒ "this payload is authentic for `shop`"

but the actual binding proven is only `HMAC(app_secret, raw_body) == received_hmac` ⇒ "this raw_body was signed by someone possessing `app_secret`" — it says nothing about which `shop` header accompanies that body. Because the webhook HMAC secret is the app's single `client_secret`/`api_secret_key`, shared across every shop that installs the app, any principal who can install the app on **any** shop (including their own, unprivileged, self-service shop) can legitimately receive a validly-signed webhook body for that shop, then resend the identical raw body with the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`, `X-Shopify-Webhook-Id`) header swapped to name a different, victim shop. `Registry.process` accepts this because it only checks the HMAC over the untouched body, then builds `WebhookMetadata` directly from the attacker-controlled headers [1](#0-0) [6](#0-5) , and dispatches it to the host application's `handler.handle(data:)` as if it were an authentic event for `data.shop`.

### Impact Explanation
The `shop` field in `WebhookMetadata` is the primary tenant identifier the gem hands to the host application's webhook handler. Because it is unauthenticated relative to the signed content, an attacker who is a legitimate (but unprivileged) merchant on the app can forge webhook events that are processed by the host application as belonging to a different tenant — a cross-tenant integrity break. Depending on what the host does with `data.shop` in `handle()` (billing state, order records, GDPR redact triggers such as `shop/redact`/`customers/redact`, sync jobs, etc.), this can corrupt or leak data belonging to other merchants, satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Requires only: (1) installing the target app on an attacker-owned/free development store to legitimately receive a signed webhook for a chosen topic, and (2) replaying the identical raw body with a swapped `shop-domain` header value to the app's webhook endpoint. No access to `api_secret_key`, TLS interception, or privileged account is needed — this is achievable by any ordinary merchant/user of the app, matching the "unprivileged internet user" threat model.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-signed material, or otherwise cryptographically bind the tenant identity to the signed body rather than trusting the `X-Shopify-Shop-Domain` header independently. At minimum, document that `WebhookMetadata#shop` is not authenticated by the HMAC and must be cross-checked by the host application against a known/installed shop list before being trusted for tenant-scoped operations.

### Proof of Concept
```ruby
# Attacker legitimately installs app on their own shop "attacker.myshopify.com"
# and receives a real, correctly-signed webhook, e.g. for "orders/create":
raw_body = '{"id":123,"note":"legit order for attacker shop"}'
valid_hmac = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)
)

# Attacker replays the SAME raw_body/HMAC but swaps the shop-domain header:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac,       # still valid! HMAC only covers raw_body
  "x-shopify-shop-domain" => "victim.myshopify.com",  # unauthenticated field
  "x-shopify-webhook-id" => "forged-id",
  "x-shopify-api-version" => "2024-01",
}

req = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(req)
# => HmacValidator.validate passes (raw_body/signature match),
#    handler.handle(data: WebhookMetadata(shop: "victim.myshopify.com", ...)) is invoked,
#    even though this event never originated from victim.myshopify.com.
```

### Citations

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
