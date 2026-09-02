### Title
Webhook `shop` field is not covered by HMAC verification, allowing shop-domain spoofing via replayed webhook body - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking the HMAC over the raw request body, then trusts the unauthenticated `x-shopify-shop-domain` header as the tenant identity passed to the app's handler.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Utils::HmacValidator.validate` computes/verifies the signature exclusively against that signable string [2](#0-1) . Meanwhile, `Request#shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, which is never part of the signed bytes [3](#0-2) . `Registry.process` verifies the HMAC and then immediately forwards `request.shop` into `WebhookMetadata`, which is handed to the app's handler as the trusted tenant identifier [4](#0-3) [5](#0-4) .

The equality broken is: *the shop identity used by the handler for tenant-scoped processing* (`WebhookMetadata#shop`, sourced from an HTTP header) is not required to equal *the shop whose bytes were actually HMAC-authenticated* (only `raw_body` is signed). Any party who can obtain one genuine `(raw_body, hmac)` pair signed with the app's shared secret — e.g., a merchant who installs the app on their own store and receives a real webhook — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value. `HmacValidator.validate` will still succeed because the header is not part of `to_signable_string`, and `Registry.process` will invoke the handler with `WebhookMetadata#shop` set to the attacker-chosen value.

### Impact Explanation
If a host application uses `WebhookMetadata#shop` to select which tenant's data to update/delete/query (a standard pattern, e.g. cancel subscription, deprovision, redact data), an attacker-controlled shop value that passed HMAC validation can cause the app to act on a different merchant's records — a cross-tenant access/integrity issue, matching the Critical impact category ("cross-tenant access").

### Likelihood Explanation
Exploitation requires the attacker to possess at least one legitimately-signed webhook body from Shopify for their own shop (trivial — they simply install the app or trigger any subscribed webhook topic on their own store), then replay that raw body/HMAC to the app's public webhook endpoint with a forged `x-shopify-shop-domain` header. No `api_secret_key`, access token, or privileged access is required — only unauthenticated HTTP access to the app's public webhook receiver, which is by design internet-reachable.

### Recommendation
Bind the shop identity into the signed payload/verification step rather than trusting the header alone, or have the library reject/flag processing unless the caller independently confirms `request.shop` matches a shop actually subscribed to that specific `webhook_id`/topic (e.g., cross-check against the app's own webhook registration records before invoking the handler, since Shopify's `webhook_id` is unique per subscription and tied to a specific shop). At minimum, document prominently that `WebhookMetadata#shop` is HMAC-unauthenticated and must not be used as the sole tenant key without additional verification (e.g. correlating `webhook_id` against previously registered subscriptions for that shop).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and registers for a webhook topic (or waits for a mandatory one to fire), receiving a real HTTP webhook request with headers `x-shopify-hmac-sha256: <valid_hmac>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: <topic>`, and some `raw_body`.
2. Attacker replays this exact `raw_body` and `x-shopify-hmac-sha256` value to the same app endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body normally [6](#0-5) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because only `raw_body` is checked [7](#0-6) .
4. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, and the app processes the webhook as if it originated from the victim's shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
