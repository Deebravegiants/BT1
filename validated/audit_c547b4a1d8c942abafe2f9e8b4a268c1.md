Confirmed: the webhook HMAC in `to_signable_string` (`lib/shopify_api/webhooks/request.rb:35-38`) signs only `@raw_body`. The `shop`, `topic`, and `webhook_id` values are read straight from HTTP headers (`shopify_header`, lines 15-33) and are never included in the signed bytes. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) validates the HMAC and then trusts `request.shop`/`request.topic` unconditionally to build `WebhookMetadata` and dispatch it to the app's handler — there is no secondary check binding the shop header to the signed payload.

### Title
Webhook shop/topic identity spoofing via HMAC that only covers the raw body - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC signature validated by `Utils::HmacValidator.validate` in `Registry.process` never binds the `shopify-shop-domain`, `shopify-topic`, or `shopify-webhook-id` headers to the signature. Any attacker who can obtain one legitimately-signed `(body, hmac)` pair — trivially available by installing the target app on their own store and receiving its webhooks — can replay that exact body/HMAC to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` (and/or `shopify-topic`) header, and the gem will accept it as authentic.

### Finding Description
The identity binding that should hold is:
`hmac_verified_bytes == bytes_used_to_identify_the_tenant_and_event`

In this gem that equality is broken:
- `hmac` is computed from `@raw_body` only (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
- `shop`, `topic`, and `webhook_id` are parsed straight out of attacker-controllable HTTP headers (`lib/shopify_api/webhooks/request.rb:15-33`) and are never part of `to_signable_string`.
- `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) does: validate HMAC over the body → look up handler by `request.topic` → invoke handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)`. Neither `shop` nor `topic` is re-validated against anything cryptographic.

Because the HMAC only proves "this body was produced by someone who knows `api_secret_key`," and does not prove "this body was produced *for shop X* or *event Y*," an attacker who has one valid `(body, hmac)` pair for their own tenant (Shop B, obtained by simply installing the app themselves — no privileged access needed) can forge an HTTP POST to the app's webhook endpoint using that same body/hmac while setting `shopify-shop-domain: shop-a.myshopify.com` (a victim shop) or a different `shopify-topic`. `Registry.process` will pass HMAC validation and hand the handler data claiming to originate from shop A, even though the signed bytes say nothing about shop A.

### Impact Explanation
This crosses the tenant boundary the report's bug class targets: "a field acted on but not covered by the HMAC" — here `shop` (and `topic`) are acted upon (used to select the handler and populate `WebhookMetadata.shop`) without being covered by the signature. Depending on what the host application's webhook handlers do with `data.shop` (e.g., look up per-shop credentials/records, trigger `shop/redact` or `customers/redact` compliance actions, or write data keyed by shop), this enables cross-tenant data confusion/injection: an attacker-controlled payload can be attributed to a victim shop, or a payload legitimately meant for topic X can be redelivered under a different registered topic Y with a different handler. This matches the High-impact bucket "cross-tenant access" achievable by an unprivileged internet user (anyone can install a public app on their own store to harvest a valid signed payload, then replay it against the same endpoint with forged headers) without needing `api_secret_key`, an access token, or any privileged account.

### Likelihood Explanation
Likelihood is realistic but not trivial: it requires (1) the attacker to legitimately install the target app (publicly available action for public apps) to harvest a genuine `(body, hmac)` pair, and (2) the app's webhook endpoint to be reachable and to trust `data.shop`/`data.topic` for authorization-sensitive logic in its handler. The gem itself provides no mitigation — `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-22`) is the only authenticity check performed, and it never touches the headers.

### Recommendation
Include the `shop`, `topic`, and `webhook_id` header values in `Webhooks::Request#to_signable_string` (or otherwise cryptographically bind them, e.g. by validating them against the shop stored for the resolved session before dispatch) so that the HMAC signature covers everything `Registry.process` acts on, not just the raw body.

### Proof of Concept
```ruby
# Step 1: Attacker installs the target app on their own shop, "shop-b.myshopify.com",
# and receives a legitimate webhook for it:
raw_body = '{"id":123,"note":"hello"}'
valid_hmac_b64 = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)
)
# headers as delivered by Shopify to the attacker's own webhook endpoint:
# "shopify-shop-domain" => "shop-b.myshopify.com"
# "shopify-hmac-sha256" => valid_hmac_b64
# "shopify-topic"       => "orders/create"

# Step 2: Attacker replays the SAME body + SAME hmac to the app's webhook endpoint,
# but forges the shop header to point at a victim shop:
forged_headers = {
  "shopify-topic" => "orders/create",
  "shopify-hmac-sha256" => valid_hmac_b64,   # unchanged, still valid because HMAC only covers raw_body
  "shopify-shop-domain" => "shop-a.myshopify.com", # victim tenant, attacker has no access to it
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (lib/shopify_api/webhooks/registry.rb:190)
# => handler.handle(data: WebhookMetadata.new(topic: "orders/create", shop: "shop-a.myshopify.com", ...))
# The app's handler now processes attacker-supplied data attributed to shop-a, a tenant
# the attacker never had access to.
``` [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
