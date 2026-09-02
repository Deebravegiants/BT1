This confirms the finding: `WebhookMetadata` carries `shop`, `topic`, `webhook_id`, and `api_version` straight from unauthenticated HTTP headers, while the gem's HMAC verification (`lib/shopify_api/webhooks/registry.rb` `process`) only covers `@raw_body` via `to_signable_string` in `lib/shopify_api/webhooks/request.rb`.

### Title
Webhook `shop` (and topic/webhook_id) attribution is not covered by HMAC verification, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body, but the shop identity that the host application uses to route/attribute the webhook payload (`request.shop`, read from the `x-shopify-shop-domain` header) is never included in the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate` computes/compares the HMAC purely against that signable string [2](#0-1) . Meanwhile, `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all pulled straight from caller-controlled HTTP headers with no cryptographic binding to the body or to each other [3](#0-2) .

`Registry.process` validates only the HMAC, then immediately trusts `request.shop` (and the other header-derived fields) to construct the `WebhookMetadata` passed to the host app's handler: [4](#0-3) . `WebhookMetadata` is a plain struct with `shop` as an unauthenticated string field [5](#0-4) .

The identity binding broken: `HMAC-verified(raw_body) == shop-attributed(raw_body)` should hold, but the gem only enforces `HMAC-verified(raw_body)`, while `shop` used for downstream tenant attribution comes from an out-of-band header the signature never covers. Because a single app's `client_secret` is shared across every shop that installs the app, any shop that installs the app (an unprivileged action available to any internet user via app install / dev store) obtains genuine `(raw_body, hmac)` pairs from its own legitimate webhook deliveries. That attacker can then replay the exact same body/HMAC pair while substituting `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) with a victim shop's domain. `Utils::HmacValidator.validate` still returns `true`, because it never inspects those headers, so `Registry.process` dispatches the forged metadata to the host application's handler as if the payload had come from the victim shop.

### Impact Explanation
This crosses the tenant boundary: a handler that uses `WebhookMetadata#shop` to select which merchant's session/store record to update (a standard usage pattern, e.g. deleting/creating resources, updating billing state, or de-provisioning a shop on `app/uninstalled`) can be tricked into applying attacker-supplied, HMAC-valid-but-shop-spoofed data against a different tenant's record. This matches the Critical "cross-tenant access" impact category since it lets one authenticated app installer inject data attributed to another merchant.

### Likelihood Explanation
Requires no secret, token, or privileged access — only that the attacker install the target app on any store they control (a normal, unprivileged install) to harvest a valid `(body, hmac)` pair, then replay it over the webhook endpoint with a forged `shop-domain` header. No TLS interception or credential theft is needed.

### Recommendation
Bind the shop (and topic/webhook_id) into the signed material, or independently verify that the shop-domain header corresponds to a shop actually associated with the `client_secret`/session used to process the webhook, before constructing `WebhookMetadata`. At minimum, document that `request.shop` is unauthenticated and host apps must not trust it without additional verification (e.g., cross-checking against a known/installed shop list).

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (unprivileged, self-service).
2. Shopify sends a legitimate webhook (e.g. `orders/create`) to the attacker's endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, and a JSON body.
3. Attacker captures the raw body and its valid HMAC.
4. Attacker (or a compromised relay under their control) sends a new HTTP request to the app's webhook route with the identical raw body and HMAC header, but with `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks the body's HMAC and returns `true` [6](#0-5) .
6. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled-but-genuinely-signed-body>, ...)` and processes it as if it originated from `victim-shop.myshopify.com`.

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
