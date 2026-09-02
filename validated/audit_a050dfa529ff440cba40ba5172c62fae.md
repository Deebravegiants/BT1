I have enough evidence to finalize this analog now.

### Title
Webhook `shop` (and `topic`/`webhook_id`) identity is trusted from unsigned headers while only the raw body is HMAC-verified, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` only validates the HMAC over the raw request body, then unconditionally trusts the `shop-domain`, `topic`, and `webhook-id` headers to build the `WebhookMetadata` passed to the host app's handler. Because these header values are not covered by the HMAC signature, any request carrying a body+HMAC pair valid for the caller's own tenant can have its `shop-domain` header rewritten to name a different shop, and the app-supplied handler will process it as an authentic webhook for that victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are all read straight from HTTP headers with no cryptographic binding to the body/HMAC: [2](#0-1) 

`Registry.process` validates only `Utils::HmacValidator.validate(request)` (i.e., HMAC over the body) and then immediately trusts `request.shop`/`request.topic`/`request.webhook_id` to construct the `WebhookMetadata` object handed to the app's handler: [3](#0-2) 

`HmacValidator.validate` computes the signature purely over `verifiable_query.to_signable_string`, i.e. the body, and compares it with `verifiable_query.hmac`: [4](#0-3) 

`WebhookMetadata.shop` is exactly the field host applications use to key their tenant data/session lookups when handling a webhook: [5](#0-4) 

**Equality that should hold but doesn't:** `shop authenticated by HMAC == shop acted upon by the handler`. In reality, the HMAC only authenticates `raw_body`, while `shop` (and `topic`/`webhook_id`) are taken from headers that are never part of the signed payload — an unprivileged actor who receives one legitimate webhook to their own shop (e.g., by installing the app on a shop they control, or through the mandatory `customers/data_request` webhook flow) obtains a body+HMAC pair valid for that body. They can then re-POST that same body/HMAC pair to the app's webhook endpoint while substituting `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`, `X-Shopify-Webhook-Id`) with a victim shop's domain. `HmacValidator.validate` still succeeds (it never inspects the headers), and `Registry.process` passes a `WebhookMetadata` claiming the victim shop as the source.

### Impact Explanation
This breaks the tenant binding the app relies on to route webhook data. A host application's handler (built against `ShopifyAPI::Webhooks::WebhookHandler`) that keys any state, cache invalidation, redaction actions, or session-triggering logic off `WebhookMetadata#shop` can be made to act on/attribute to a shop the attacker doesn't own — a cross-tenant integrity issue. This satisfies the Critical "cross-tenant access" impact category, since the vulnerability lets one tenant force write/administrative actions to be attributed to another tenant purely by controlling headers, with no valid credential for the victim shop.

### Likelihood Explanation
Likelihood is high for the mandatory/self-triggerable topics (`customers/data_request`, `customers/redact`, `shop/redact`) and standard shop-lifecycle webhooks: any developer/merchant can install the app on their own store, capture a genuine valid `(body, hmac)` webhook delivery, and replay it against the app's public webhook endpoint with a forged `shop-domain` header — no secret material (`api_secret_key`, access token) is required, only observation of one's own legitimately-received webhook.

### Recommendation
Bind the trusted identity fields into the signed payload validated against the HMAC, e.g. include `topic`, `shop`, and `webhook_id` header values in `to_signable_string` (mirroring what Shopify actually authorizes for the delivery), or otherwise cross-check the `shop-domain` header against an out-of-band trusted source (e.g., only accept webhooks for shops with an active, previously-registered session) before constructing `WebhookMetadata`. At minimum, document to consumers that `WebhookMetadata#shop`/`#topic`/`#webhook_id` are unauthenticated and must not be trusted for tenant-scoping decisions without additional verification.

### Proof of Concept
```ruby
# Attacker legitimately installs the app on their own shop "attacker.myshopify.com"
# and receives (or synthetically computes, since HMAC only covers the body) a valid webhook:
body = '{"id":1}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, body)

# Attacker forges the shop-domain header to point at a victim shop they do NOT control:
headers = {
  "x-shopify-topic" => "customers/data_request",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # not the attacker's shop
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: headers)

# HMAC validation succeeds because it only checks the body, not the shop header:
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(topic: "customers/data_request",
#      shop: "victim-shop.myshopify.com", body: {"id"=>1}, ...))
# The host app's handler now believes this authentic-looking webhook came from victim-shop.
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
