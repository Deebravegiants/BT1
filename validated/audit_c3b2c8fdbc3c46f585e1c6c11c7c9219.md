Confirmed root cause: `ShopifyAPI::Webhooks::Request#hmac` validates only the raw request body via `to_signable_string` returning `@raw_body`, while `shop` is read straight from the unauthenticated `X-Shopify-Shop-Domain`/`shopify-shop-domain` header with no cryptographic binding to that HMAC. `Registry.process` passes this unauthenticated `request.shop` straight into `WebhookMetadata`, which host apps use to route/attribute the incoming data to a merchant/tenant. [1](#0-0) [2](#0-1) 

### Title
Webhook shop-domain header is unauthenticated and unbound to the HMAC, enabling cross-tenant webhook data attribution - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string solely from the raw JSON body, while the `shop` value passed to app webhook handlers comes from the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header, which is never included in the signed data. Any party who possesses one validly-signed webhook payload (e.g. from their own store, on which they can install the target app or any app that reuses this delivery to their endpoint) can replay that payload to the victim app's webhook endpoint with an arbitrary `shop-domain` header while keeping the original body and HMAC unchanged. `HmacValidator.validate` still passes because it only checks the body, so the app's `WebhookHandler` receives attacker-supplied webhook `body` content falsely attributed to any `shop` value the attacker chooses, breaking the equality `shop authenticated by the signature == shop used by the app to key its per-tenant data`.

### Finding Description
`Utils::HmacValidator.validate` verifies `verifiable_query.to_signable_string`, and for `Webhooks::Request` this method returns only `@raw_body`: [3](#0-2) 

Meanwhile `Webhooks::Request#shop` is read directly from a header dictionary populated straight from the incoming HTTP headers, with no involvement in the signature: [4](#0-3) [5](#0-4) 

`Registry.process` validates the HMAC and then forwards `request.shop` unmodified into `WebhookMetadata`, which is the only shop identifier the app-provided `WebhookHandler` implementation receives to decide which merchant/tenant record the webhook body applies to: [2](#0-1) [6](#0-5) 

Because the signature covers only the body bytes, the pair `(raw_body, hmac)` remains valid for *any* value of the `shop-domain` header. An attacker who can obtain one legitimately-signed webhook delivery (trivial: install the target public app on their own store, or any store they control, and capture the webhook Shopify sends) can resend that exact `(body, hmac)` pair to the app's webhook endpoint while substituting a different shop's domain in the header. `HmacValidator.validate` will still return `true`, and the handler will process the attacker's body as if it belongs to the victim shop.

### Impact Explanation
This breaks the tenant-isolation boundary the HMAC is meant to enforce: the shop identity that the signature actually authenticates (via body-embedded fields, if any) is not the same as the shop identity the app trusts for record-keying (`data.shop`). Depending on how the host app uses `data.shop` (e.g. to look up which merchant's order/customer/inventory record to create or update, or to select which access token/session to act with), an attacker-controlled cross-tenant write or data-confusion primitive is possible without ever needing the app's `client_secret`, an access token, or any privileged credential — only a normal installation of the app on an attacker-controlled store.

### Likelihood Explanation
Any user who can install the target app on their own development/test store (a routine, unprivileged action for public Shopify apps) can capture one authentic `(raw_body, hmac)` pair from a real webhook delivery and replay it against the app's public webhook endpoint with a forged `shop-domain` header. No secret material or privileged access is required beyond normal app installation, making this readily reachable by an unprivileged internet user.

### Recommendation
Include the shop domain (and ideally topic/webhook id/api version) inside the HMAC-signed material, or have `WebhookHandler` implementations derive the shop strictly from a value embedded and verified within the signed body/payload rather than from an unauthenticated header. At minimum, document prominently that `request.shop` is not authenticated by the HMAC and must not be trusted for tenant-keying without additional verification (e.g., cross-checking against a known/registered shop for that webhook subscription).

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and registers/observes a legitimate webhook delivery for a subscribed topic, capturing the raw JSON `body` and the `X-Shopify-Hmac-Sha256` header value (`hmac`) sent by Shopify — both valid and signed with the app's real secret.
2. Attacker sends a new HTTP POST to the app's webhook endpoint with the exact same `body` and `X-Shopify-Hmac-Sha256` header, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. Server constructs `ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: forged_headers)` and calls `ShopifyAPI::Webhooks::Registry.process(request)`.
4. `Utils::HmacValidator.validate(request)` succeeds because `to_signable_string` only checks `raw_body`, which is unchanged: [7](#0-6) [3](#0-2) 
5. `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` is invoked with `shop == "victim-shop.myshopify.com"`, even though the body content originated from `attacker.myshopify.com`'s own webhook, demonstrating the unauthenticated cross-tenant shop-attribution.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-21)
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
```
