### Title
Webhook `shop`/`topic`/`webhook_id`/`api_version` fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` accepts the request as long as the body's HMAC is valid, then hands the header-derived (unsigned) `shop` value to the app's `WebhookHandler` as trusted tenant identity. This breaks the equality `shop authenticated-by-HMAC == shop acted-on-by-handler`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from HTTP headers with no cryptographic binding: [2](#0-1) 

`HmacValidator.validate` only ever calls `to_signable_string`, so it validates the body bytes, never the headers: [3](#0-2) 

`Registry.process` trusts this unauthenticated `request.shop` and forwards it directly into `WebhookMetadata`, which is the only tenant-identifying field passed to the app's handler: [4](#0-3) [5](#0-4) 

Because the signature only certifies "this body byte-string was produced with our shared secret," and never certifies "for shop X" or "for topic Y," any two webhook deliveries with an identical (or attacker-reproducible) raw body — for example a `shop/redact` or `customers/data_request` payload the attacker can trigger for a shop they legitimately control/install the app on — will produce a valid HMAC regardless of which `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, `X-Shopify-Webhook-Id`, or `X-Shopify-Api-Version` header values accompany it. An attacker who can reach the app's public webhook endpoint (this is typically an unauthenticated HTTP endpoint by design) can replay a validly-HMAC'd body they obtained (e.g., from a webhook delivered to their own store) while substituting the `shop-domain` header for a victim shop, and the library will report it as an authentic webhook for the victim shop.

### Impact Explanation
This is a cross-tenant identity confusion: the library authenticates the payload bytes but not the shop/topic binding that host applications rely on to select the correct tenant record, secret, or business logic (per the library's own documented `WebhookMetadata.shop` contract). A host application built exactly per this gem's documented API (`ShopifyAPI::Webhooks::Registry.process` → `WebhookHandler#handle(data:)`) will act on `data.shop` believing it was authenticated by `Utils::HmacValidator.validate`, when in fact only the body was authenticated. This matches the "Critical - cross-tenant access" impact class: an attacker can cause the app to execute shop-scoped side effects (e.g., GDPR redaction, data deletion, order/customer processing) attributed to a shop the attacker does not control, using material the attacker obtained legitimately for a different (their own) shop.

### Likelihood Explanation
Requires only: (1) the attacker to install/operate the target app on a shop they control (trivial for any public app), (2) network access to the app's public webhook endpoint (by design, unauthenticated), and (3) the ability to replay an HTTP request with a modified header while keeping the previously-received valid body/HMAC pair intact. No possession of `api_secret_key`, access tokens, or any privileged credential is required — the attacker uses their own legitimately-issued webhook to attack another tenant. This is a realistic, moderately likely path given the library never authenticates the header fields at all.

### Recommendation
Include the identity-binding fields (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed content, or otherwise cryptographically bind them to the payload before exposing `WebhookMetadata` to handlers, so `HmacValidator.validate` certifies the full tuple `(shop, topic, body)` rather than the body alone. At minimum, document prominently that `request.shop`/`request.topic` are unauthenticated and must not be trusted for tenant selection, and consider deriving the shop identity from the `Registry`'s own `Session`/registration information rather than header replay whenever cross-checking is possible.

### Proof of Concept
```ruby
# 1. Attacker installs the target app on their own shop "attacker.myshopify.com"
#    and receives a legitimately signed webhook, e.g. for topic "customers/data_request":
raw_body = '{"shop_id":111,"shop_domain":"attacker.myshopify.com","customer":{...}}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), api_secret_key, raw_body)

# 2. Attacker replays the SAME body + HMAC to the app's public webhook endpoint,
#    but swaps only the shop-domain header to the victim's shop:
headers = {
  "x-shopify-topic" => "customers/data_request",
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",  # attacker-controlled, unsigned
  "x-shopify-webhook-id" => "attacker-chosen-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)

# 3. HmacValidator.validate(request) returns true, because it only checks raw_body,
#    which the attacker legitimately possesses/signed for their OWN shop:
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

# 4. Registry.process dispatches to the handler with data.shop == "victim-shop.myshopify.com",
#    even though the payload/signature never authenticated that shop:
ShopifyAPI::Webhooks::Registry.process(request)
# handler.handle(data: WebhookMetadata.new(topic: "customers/data_request",
#   shop: "victim-shop.myshopify.com", body: ..., ...))
``` [6](#0-5)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
