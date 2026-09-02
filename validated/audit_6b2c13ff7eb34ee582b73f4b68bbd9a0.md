Confirmed: the HMAC for webhook requests is computed only over `to_signable_string`, which returns `@raw_body` [1](#0-0) , while `topic`, `shop`, `api_version`, and `webhook_id` are all pulled straight from HTTP headers with no cryptographic binding to that HMAC [2](#0-1) . `Registry.process` validates only `Utils::HmacValidator.validate(request)` (i.e., body vs. secret) and then dispatches the handler using the unauthenticated `shop`/`topic`/`webhook_id` header values [3](#0-2) .

### Title
Webhook tenant identity (`shop`, `topic`, `webhook_id`) not covered by HMAC, allowing cross-tenant replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity using only the raw request body against the `X-Shopify-Hmac-Sha256` header, while the `shop`, `topic`, and `webhook_id` values used downstream to attribute the webhook to a specific merchant/tenant are read directly from unauthenticated headers.

### Finding Description
`Request#to_signable_string` returns `@raw_body` only [1](#0-0) . `HmacValidator.validate` computes the HMAC solely over this signable string and compares it to the `hmac` header value [4](#0-3) . Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are read from the `shopify-shop-domain`, `shopify-topic`, `shopify-api-version`, and `shopify-webhook-id` headers respectively, none of which are included in the signed material [2](#0-1) . `Registry.process` accepts the request once the body HMAC checks out, then builds `WebhookMetadata` and dispatches to the app's handler using those unauthenticated `shop`/`topic`/`webhook_id` values [5](#0-4) .

This breaks the intended identity binding: `HMAC-verified sender == shop the app attributes the payload to`. Because Shopify computes the HMAC over the body only, any legitimately-signed webhook body (e.g., one an attacker generates for their own store, since anyone can install an app on their own dev/trial shop and receive genuinely signed webhooks) carries a valid HMAC that stays valid regardless of which `shop`, `topic`, or `webhook_id` header accompanies it. An attacker who controls the HTTP request reaching the app's webhook endpoint (e.g., through the app's own public endpoint, since nothing in the gem ties headers to the signed body) can pair a validly-signed body from their own shop with a forged `shopify-shop-domain` header naming a victim shop, and the gem will treat it as an authentic, verified webhook for that victim shop.

### Impact Explanation
If the host application uses `WebhookMetadata#shop` (as returned by this gem after a passing HMAC check) to select the tenant record to update — which is the documented, expected usage pattern of `Registry.process`/`WebhookMetadata` — an attacker can inject data into, or trigger tenant-scoped side effects for, a shop they don't own, using a genuinely-signed body sourced from a shop they do control. This is a cross-tenant access primitive: the gem's own verification step (`Utils::HmacValidator.validate`) reports "valid" while the tenant-identifying field it hands to the caller was never authenticated.

### Likelihood Explanation
Any unprivileged internet user can install the app on a shop they control (e.g., a free Shopify development store), capture a real, validly-HMAC'd webhook payload for that shop, and replay it to the app's public webhook endpoint with the `shopify-shop-domain` (and/or `shopify-topic`/`shopify-webhook-id`) header rewritten to reference a different, victim shop. No access to `api_secret_key`, tokens, or the victim's credentials is required — only the ability to send an HTTP request to the app's already-public webhook receiver.

### Recommendation
Bind the tenant-identifying fields into the signed material verified by `HmacValidator`, or otherwise cryptographically tie `shop`/`topic`/`webhook_id` to the HMAC-covered body (e.g., by including them in `to_signable_string`, or by requiring the caller to independently re-verify that the `shop` header matches an app-known, previously-authenticated shop for that specific `webhook_id`/subscription before trusting `WebhookMetadata#shop`).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a shop they legitimately control) and triggers a webhook, obtaining a raw body `B` and a genuine `X-Shopify-Hmac-Sha256: H` computed by Shopify over `B` with the app's real `client_secret`.
2. Attacker sends a POST to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid), but `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and, if relevant, a `X-Shopify-Webhook-Id`/topic of their choosing).
3. `ShopifyAPI::Webhooks::Request.new` parses these headers without objection [6](#0-5) , `Utils::HmacValidator.validate(request)` succeeds because it only checks `B` against `H` [7](#0-6) , and `Registry.process` dispatches the handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)` [5](#0-4) .
4. The app's handler, trusting the gem's HMAC-verified `WebhookMetadata#shop`, processes/persists the attacker-controlled body under the victim shop's tenant context.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
