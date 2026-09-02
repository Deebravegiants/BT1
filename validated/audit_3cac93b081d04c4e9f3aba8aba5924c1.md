Confirmed: the webhook `hmac` in `lib/shopify_api/webhooks/request.rb` is computed only over `to_signable_string` (the raw body), while `shop` and `topic` are read directly from unauthenticated HTTP headers. This is the analog to the reported bug class: a field that is *acted on* (the `shop` attribution used for tenant routing) is not covered by the HMAC that is verified.

### Title
Webhook `shop` (and `topic`) attribution is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives its HMAC-signable content solely from the raw request body, but the `shop` (and `topic`) values used to route and attribute the webhook to a specific merchant are taken from HTTP headers that play no part in that signature. `ShopifyAPI::Webhooks::Registry.process` validates only the body's HMAC and then trusts the header-derived `shop` value when dispatching to the app's handler.

### Finding Description
`Utils::HmacValidator.validate` computes the expected signature from `verifiable_query.to_signable_string` and compares it to the `hmac` value supplied by the caller: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw HTTP body: [2](#0-1) 

But `shop`, `topic`, `api_version`, and `webhook_id` are all pulled directly from HTTP headers, none of which are included in the signed content: [3](#0-2) 

`Registry.process` validates the HMAC of the body and, once that check passes, unconditionally trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` object passed to the app's handler: [4](#0-3) 

The identity binding broken here is: `shop_verified_by_hmac == shop_used_by_handler` should hold, but in fact `hmac` only authenticates `raw_body`, so `request.shop` (header) is unauthenticated with respect to the signature. Because Shopify signs webhooks per-app (the same `client_secret`/HMAC key is used for every shop that has the app installed), any merchant who installs the app can receive a legitimately-signed webhook for their *own* store (e.g. a generic `app/uninstalled` or other webhook whose body content is fixed/predictable or attacker-influenced, such as an order note or product title the attacker controls under their own shop). That merchant can then replay the same raw body and valid HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop. The signature still validates because it never covered the header, and `Registry.process` will call the handler with `shop: <victim-shop>` even though the body actually originated from the attacker's own store.

### Impact Explanation
This allows a merchant with a completely unprivileged, self-service installation of the app (no access token, no `client_secret`, no server compromise) to make the app process arbitrary attacker-controlled payloads under an arbitrary victim `shop` domain. Depending on how the host application uses `WebhookMetadata#shop` (e.g., looking up/creating tenant records, updating per-shop settings, triggering shop-scoped side effects, or deciding `shop/redact`/`customers/redact` compliance actions), this enables cross-tenant data injection or state corruption attributed to a shop the attacker does not control — matching the "Critical: cross-tenant access" impact category, since a shop-identity check (verified `shop` vs. `shop` acted upon) is bypassed.

### Likelihood Explanation
Likelihood is high for any app: an attacker only needs to be a legitimate merchant that installs the target Shopify app (a normal, unprivileged action), capture one legitimately-delivered webhook (body + valid HMAC) from their own store, and resend it to the app's public webhook endpoint with a forged `shop-domain` header. No `api_secret_key`, access token, or elevated privilege is required — the whole point of the bug is that the header is *not* covered by the secret-derived HMAC.

### Recommendation
Bind the `shop` (and ideally `topic`) values into the signed content, or otherwise cryptographically tie them to the payload before trusting them for routing/attribution — e.g., have `to_signable_string` incorporate the shop header, or cross-check the `shop` domain against an independently-verified identifier (such as looking up the webhook by its Shopify-issued `webhook_id`/subscription rather than trusting the header directly). At minimum, document that consuming applications must not treat `WebhookMetadata#shop` as authenticated unless additional verification is performed.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`.
2. Trigger a webhook delivery (e.g. any topic with attacker-influenced content) and capture the raw POST body plus the `X-Shopify-Hmac-Sha256` header — both legitimately signed by Shopify using the app's `client_secret`.
3. Replay the exact same body and HMAC header to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body successfully: [5](#0-4) 
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the HMAC — unaffected by the spoofed `shop` header: [6](#0-5) 
6. The registered handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and the attacker's payload, even though the victim shop never sent this webhook.

### Citations

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
