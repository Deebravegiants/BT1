### Title
Webhook `shop-domain` and `topic` headers are trusted but not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable content solely from the raw request body, while the `shop`, `topic`, and `webhook_id` values — all derived from unauthenticated HTTP headers — are handed unchanged to the app's webhook handler as trusted metadata. This breaks the intended binding `HMAC-covers(shop, topic, body) == fields-trusted-by-handler(shop, topic, body)`; only `body` is actually covered.

### Finding Description
`Utils::HmacValidator.validate` verifies a request by comparing a computed HMAC over `verifiable_query.to_signable_string` against the supplied HMAC value: [1](#0-0) 

For webhook requests, `Request#to_signable_string` returns only the raw body — it does not include the `shop-domain`, `topic`, or `webhook-id` headers: [2](#0-1) 

`Registry.process` validates the HMAC over the body, then immediately trusts `request.topic` to select the handler and `request.shop` (plus `request.webhook_id`, `request.api_version`) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`WebhookMetadata` carries `shop`, `topic`, and `webhook_id` verbatim into the app's business logic, with no indication that these fields were unauthenticated: [4](#0-3) 

Because the HMAC is computed only over the raw body, any HTTP request that presents a *previously valid* `(raw_body, hmac)` pair — which any shop that has the app installed will legitimately receive for its own webhooks — remains "valid" per `HmacValidator.validate` even if the `shop-domain` and `topic` headers are swapped for arbitrary values. The gem provides no mechanism to bind the headers to the signed payload, so the app-level handler ends up trusting a `shop` value and `topic` value that were never authenticated by Shopify's signature, only the body was.

### Impact Explanation
This is a cross-tenant identity-binding failure: the equality that should hold, `hmac_signed(shop, topic, webhook_id, body) == trusted_by_handler(shop, topic, webhook_id, body)`, does not hold — only `body` is signed. A party that legitimately receives one authentic webhook (e.g., the operator of any shop that has installed the app, who can observe the `raw_body`/`x-shopify-hmac-sha256` pair delivered to their own endpoint or reverse proxy) can resubmit that exact body+HMAC pair to the app's webhook endpoint with a forged `shop-domain` header naming a different, victim merchant, and/or a forged `topic` header selecting a different handler. Since `Registry.process` uses these unauthenticated header values to route to a handler and to populate `WebhookMetadata.shop`/`.topic`/`.webhook_id` for that handler, an app that keys any tenant-scoped action off `data.shop` (as the gem's own documentation/interface encourages, since `shop` is the only tenant identifier `WebhookMetadata` exposes) can be made to attribute or apply the payload's contents to the wrong shop, or process a body under an unintended topic-specific code path. This matches the Critical "cross-tenant access" category, since it lets one tenant/attacker cause the app to treat delivered data as belonging to a different tenant using only its own legitimately obtained HMAC, without ever needing the app's `client_secret` or a merchant access token.

### Likelihood Explanation
Any developer/merchant who installs the app on their own store can trivially capture a genuine `(raw_body, x-shopify-hmac-sha256)` pair (it is delivered to their own server or can be intercepted at their own reverse proxy since it is not TLS-secret-dependent to read once received), then replay it directly against the app's public webhook endpoint with modified `shop-domain`/`topic` headers. No secret material, privileged account, or social engineering is required beyond operating one's own shop instance of the app — a normal, unprivileged use path.

### Recommendation
Include the identity-binding headers in the HMAC-signed content used for verification, or otherwise cryptographically bind them: e.g., have `Request#to_signable_string` (or a webhook-specific verification routine) incorporate `shop`, `topic`, and `webhook_id` alongside `raw_body` before computing/comparing the HMAC, so that any tampering with those headers invalidates the signature. At minimum, document clearly that `WebhookMetadata.shop`/`.topic`/`.webhook_id` are not covered by the HMAC and must not be used for tenant-scoped decisions without additional verification (e.g., cross-checking against a known/registered shop list per webhook subscription).

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and lets Shopify send a legitimate webhook, e.g., `orders/create`, capturing the raw body `B` and the header `x-shopify-hmac-sha256: H` (valid because `H = HMAC-SHA256(api_secret_key, B)`), as verified by: [5](#0-4) 
2. Attacker sends a new HTTP request to the app's webhook endpoint with the same body `B` and header `H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and/or `x-shopify-topic: shop/redact`.
3. `Request.new` accepts the forged headers as long as the required header names are present: [6](#0-5) 
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H`, then dispatches using the forged `topic` and constructs `WebhookMetadata` with the forged `shop`: [3](#0-2) 
5. The app's `WebhookHandler#handle` implementation receives `data.shop == "victim-shop.myshopify.com"` and `data.topic == "shop/redact"` for body `B`, despite neither value ever having been authenticated by Shopify's signature — demonstrating the broken binding between HMAC-verified bytes and the fields the handler trusts.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L33-40)
```ruby
        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
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
