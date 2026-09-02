### Title
Webhook shop-domain and topic headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from unauthenticated HTTP headers [2](#0-1) . `Utils::HmacValidator.validate` only recomputes the HMAC over `to_signable_string` (the body) and compares it to the `hmac-sha256` header [3](#0-2) . The `shop` field is therefore accepted and forwarded to the handler without being bound by the signature that supposedly authenticates the request.

### Finding Description
`Registry.process` gates webhook handling solely on `Utils::HmacValidator.validate(request)` [4](#0-3) . That validation only proves the raw body byte string was signed with the app's shared `client_secret`; it says nothing about which shop or topic the signer intended, because those come from separate, unsigned headers (`x-shopify-shop-domain`, `x-shopify-topic`) [5](#0-4) .

Because a single app uses one shared `client_secret` (or `old_api_secret_key`) to sign webhooks for *every* installed shop [6](#0-5) , any merchant who installs the app can legitimately trigger a webhook, capture the resulting valid `(raw_body, x-shopify-hmac-sha256)` pair from their own shop, then replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value (e.g., a victim shop's domain) and/or a different `x-shopify-topic`. `HmacValidator.validate` still succeeds because it never inspects those headers, and `Registry.process` passes the attacker-chosen `request.shop` straight into `WebhookMetadata` handed to the app's handler [7](#0-6) .

The broken identity binding is: `shop` used by the host application to attribute/act on the webhook (session lookup, tenant-scoped writes, etc.) ≠ `shop` that actually produced the HMAC-covered bytes. The gem's contract implies "HMAC valid ⇒ trustworthy sender for this shop/topic," but the signature only covers the body.

### Impact Explanation
This is a cross-tenant identity confusion: an unprivileged internet user who can install the app on any store (even a free/trial install) can forge webhook deliveries that appear to originate from a shop they do not control, since the shop attribution is unauthenticated. Any host application that trusts `WebhookMetadata#shop` (returned by this gem) to select the tenant/session/access-token context for processing the (attacker-controlled) body will process or store attacker data under another merchant's identity — a cross-tenant access impact.

### Likelihood Explanation
Likelihood is significant for any app that registers a webhook topic and lets a real merchant install it: the attacker only needs to be able to trigger any one webhook to their own shop (installation, order, product update, etc.), capture the body + signature from their own delivery, and resend the HTTP request with an edited `x-shopify-shop-domain` header. No access token, `client_secret`, or privileged account is required — only ordinary use of the app as a merchant.

### Recommendation
Bind the shop (and ideally topic) into the signed material actually verified, not just trust headers: require the host application to independently confirm `request.shop` corresponds to a shop for which the app holds an active session/installation, and/or extend `VerifiableQuery`/`HmacValidator` so shop and topic are covered by an application-level check (e.g., cross-referencing `shop` against known installed shops before dispatching) rather than relying solely on `Utils::HmacValidator.validate`, whose `to_signable_string` only spans the raw body.

### Proof of Concept
1. Install the target app on attacker-controlled store `attacker.myshopify.com`; trigger any registered webhook topic, capturing the raw POST body and `X-Shopify-Hmac-Sha256` header (both signed correctly with the app's real `client_secret`).
2. Replay the identical raw body and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `X-Shopify-Topic`).
3. `ShopifyAPI::Webhooks::Request.new` accepts the headers [8](#0-7) ; `Utils::HmacValidator.validate(request)` succeeds because it only recomputes the HMAC over `@raw_body` [3](#0-2) .
4. `Registry.process` dispatches to the registered handler with `WebhookMetadata` carrying `shop: "victim-shop.myshopify.com"` and the attacker's body content [9](#0-8) , causing the host application to process attacker-controlled data under the victim shop's tenant context.

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
