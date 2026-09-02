### Title
Webhook Shop/Topic Identity Not Bound to HMAC Signature Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `Registry.process` validates the HMAC over the body only and then dispatches the handler using the header-derived `shop`, breaking the binding between "bytes verified by HMAC" and "tenant identity trusted for the callback."

### Finding Description
`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`, and for webhooks that method returns only `@raw_body`: [1](#0-0) [2](#0-1) 

`shop`, `topic`, `webhook_id`, and `api_version` are all sourced straight from caller-supplied headers (`shopify-shop-domain`, `shopify-topic`, etc.) and are never part of the signed content: [3](#0-2) [4](#0-3) 

`Registry.process` validates the HMAC (over body only) and then immediately trusts `request.shop` and `request.topic` to route and label the payload passed to the app's handler: [5](#0-4) 

Because the shared secret (`Context.api_secret_key`) used to sign webhooks is the same for every shop that has installed the app, and because the `shop-domain` header is excluded from the signable string, a valid HMAC only proves "this body was signed by Shopify for this app" — it proves nothing about which shop the webhook is attributed to. Any party who can obtain one genuinely signed webhook delivery for an app (e.g., by installing the app themselves, a legitimate action) can replay that same body/HMAC pair while swapping the `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`) header value to any other shop string. `Registry.process` will still pass HMAC validation and will hand the handler a `WebhookMetadata`/equivalent record claiming to be from the victim shop, which the host application typically uses as the tenant key for session/database lookups.

This matches the "field acted on but not covered by the HMAC" analog class: the shop identity that downstream code treats as the authenticated caller is not the same value that the HMAC actually protects.

### Impact Explanation
Host applications built on this gem commonly key their persistence and business logic (session retrieval, mandatory compliance webhooks like `shop/redact`, `customers/redact`, `customers/data_request`, order/customer sync, etc.) off `WebhookMetadata#shop`/`request.shop` under the assumption that a passing HMAC check means the whole request — including shop attribution — is authentic. Since shop is not covered by the signature, an attacker with any legitimate installation of the target app can forge cross-tenant webhook deliveries, causing the app to act on/write to another merchant's data under a webhook it believes came from that merchant. This is a cross-tenant integrity/access issue.

### Likelihood Explanation
Exploitation only requires installing the target app on the attacker's own shop (a normal, low-privilege action) to obtain one validly HMAC-signed webhook delivery, then replaying the same body with a substituted `shop-domain` header value at the app's webhook endpoint. No access token, `client_secret`, or privileged credential is needed.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the signed/verifiable content used for webhook trust decisions, or otherwise cryptographically bind the header-derived shop identity to the payload before handing it to the registered handler — e.g., require the host application to cross-check `request.shop` against the shop associated with the session/subscription that originally registered the webhook, and document this requirement prominently since the header itself carries no authenticity guarantee from the HMAC check alone.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`, triggering a real webhook delivery, e.g. `orders/create`, with a valid `X-Shopify-Hmac-Sha256` computed over the JSON body using the app's shared secret.
2. Attacker captures the raw body and HMAC header value.
3. Attacker POSTs the identical body/HMAC to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the (attacker-controlled but validly signed) body against the shared secret: [6](#0-5) 
5. The handler receives `shop: "victim.myshopify.com"` despite the payload never having been signed for or delivered about that shop, and the host app processes it as an authentic event for the victim tenant.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-70)
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

      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
