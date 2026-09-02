### Title
Webhook tenant identity (`shop`) is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable string from the raw body only, while the `shop` field that the library hands to the app's webhook handler as the tenant identifier is read straight from an unauthenticated header. This breaks the implicit binding `hmac == HMAC(secret, body ++ shop)` that the OAuth `AuthQuery` maintains (there, `shop` is explicitly part of `to_signable_string`), and allows a valid HMAC/body pair obtained for one shop to be replayed against a different shop identity.

### Finding Description
`Utils::HmacValidator.validate` verifies a `VerifiableQuery` by recomputing `HMAC(secret, to_signable_string)` and comparing it to the object's `hmac` attribute: [1](#0-0) 

For `ShopifyAPI::Auth::Oauth::AuthQuery`, `to_signable_string` explicitly binds `shop` (along with `code`, `host`, `state`, `timestamp`) into the signed payload: [2](#0-1) 

But `ShopifyAPI::Webhooks::Request` signs only the raw body, while `shop` (and `topic`, `webhook_id`, `api_version`) are pulled unauthenticated from the `X-Shopify-Shop-Domain` / `shopify-shop-domain` header: [3](#0-2) 

`Registry.process` only validates the HMAC over the body and then forwards the header-derived `request.shop` straight into `WebhookMetadata`, which is delivered to the app's handler as the trusted tenant identity: [4](#0-3) [5](#0-4) 

Because an app's `client_secret`/`api_secret_key` is the same value shared across every shop that installs the app (it is not per-tenant), a body+HMAC pair that is legitimately generated for one shop remains cryptographically valid when replayed with a different `shop-domain` header. The equality the gem should enforce is `hmac == HMAC(secret, body, shop)`; instead it enforces only `hmac == HMAC(secret, body)`, while `shop` — the value used downstream for tenant scoping — is asserted by evaluating `shop == header value` without that header ever being covered by the signature.

### Impact Explanation
An unprivileged internet user who can obtain any one genuine, HMAC-signed webhook delivery for a shop they control (e.g., by installing the app on their own free/dev store and triggering an event) can resend the exact same body and HMAC to the app's public webhook endpoint while substituting the `shop-domain` header with a victim shop's domain. `HmacValidator.validate` still passes because it never inspects the header. The application's `WebhookHandler#handle` then receives `WebhookMetadata` whose `shop` field is attacker-controlled but appears library-verified, letting the attacker inject or trigger tenant-scoped actions (e.g. order creation records, `customers/redact`, `shop/redact`, `app/uninstalled` handling) attributed to the victim's tenant — i.e., cross-tenant access, without ever needing the app's real credentials, an access token, or TLS interception.

### Likelihood Explanation
Webhook endpoints are public HTTP endpoints by design, requiring no authentication to reach. The only prerequisite is obtaining one legitimately-signed webhook for any shop (trivially available to any developer/merchant who installs the app on their own store), after which forging the tenant header on replay requires no secret knowledge. This is fully reachable through the gem's documented API (`ShopifyAPI::Webhooks::Request.new` + `Registry.process`) exactly as intended to be used by host applications.

### Recommendation
Bind the tenant identity into the verified payload instead of trusting an unauthenticated header: include `shop` (and ideally `topic`/`webhook_id`) in the HMAC-covered signable string, or otherwise cryptographically bind the header value to the request (e.g., verify it against session/registration state established when the webhook was registered) before constructing `WebhookMetadata`. At minimum, document that `request.shop` must not be treated as authenticated by `Registry.process` and require host apps to cross-check it against known registered shops.

### Proof of Concept
```ruby
# 1. Attacker installs the app on their own shop and captures a real webhook delivery:
#    raw_body = '{"id":1,...}'
#    valid_hmac = Base64.encode64(OpenSSL::HMAC.digest("sha256", app_secret, raw_body))
#    headers include "x-shopify-shop-domain" => "attacker-shop.myshopify.com"

# 2. Attacker replays the identical body + hmac, but swaps the shop header:
forged_headers = {
  "x-shopify-topic"        => "orders/create",
  "x-shopify-hmac-sha256"  => valid_hmac,          # unchanged, still valid for raw_body
  "x-shopify-shop-domain"  => "victim-shop.myshopify.com", # forged, not covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# 3. HMAC validation succeeds because it only checks raw_body:
ShopifyAPI::Utils::HmacValidator.validate(request) #=> true

# 4. Registry.process hands the forged shop straight to the app's handler:
ShopifyAPI::Webhooks::Registry.process(request)
# handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
```

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-24)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end

    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
        abstract.params(data: WebhookMetadata).void
      end
      def handle(data:); end
    end
```
