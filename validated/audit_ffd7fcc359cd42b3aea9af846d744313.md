### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) header not covered by HMAC verification allows cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body. The `shop` (and `topic`, `webhook_id`, `api_version`) values are read straight from unauthenticated HTTP headers and are handed to the host application's handler as the trusted tenant identifier, even though those headers are never part of the signed payload. An attacker who legitimately controls one shop can replay a genuinely-signed webhook while swapping the `shop-domain` header to point at a victim shop, and the signature check still passes.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines the signable string as only the raw body: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are all derived from HTTP headers that are outside this signed string: [2](#0-1) 

`Utils::HmacValidator.validate` recomputes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e., the raw body) and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` trusts this check and then forwards the unauthenticated `request.shop` and `request.topic` values straight into the handler as the tenant/topic binding: [4](#0-3) 

This breaks the intended identity binding: `shop header == tenant the payload is attributed to` should equal `shop the HMAC secret proves the payload originated from`. Because only the body bytes are covered by the HMAC, that equality is never enforced — any bytes labeled as coming from a shop are accepted as long as *some* valid body/HMAC pair exists, regardless of which shop header accompanies it. This mirrors the reported Chainlink-oracle bug class: "a field acted on (`shop`) but not covered by the [HMAC]."

Every shop that installs an app shares the same `client_secret`/`api_secret_key` for HMAC computation across all Shopify webhook subscribers. Consequently, a webhook that Shopify legitimately signs for a shop the attacker controls has a body/HMAC pair that is also valid for a forged request bearing a *different* shop's domain header, since the shop identity itself is never part of the signed material.

### Impact Explanation
This allows a malicious but otherwise unprivileged app-installer (a "shop" tenant using the same multi-tenant app) to make the host application process attacker-supplied webhook payloads while attributing them to an arbitrary victim shop — a cross-tenant access/data-poisoning primitive achieved without ever possessing the victim's access token or the app's `client_secret`. Depending on how the host app's webhook handler keys off `WebhookMetadata#shop`, this can lead to corrupting another tenant's order/customer records, triggering shop-scoped side effects (e.g. fulfillment, notifications, GDPR/compliance flows) under the victim's identity, or bypassing tenant isolation assumptions the host app relies on this gem to provide.

### Likelihood Explanation
Reasonably likely for any real-world multi-tenant Shopify app: the attacker only needs to install the app on their own store (a normal, unprivileged action) to obtain a genuinely-signed webhook body/HMAC pair, then replay it to the app's public webhook endpoint with a modified `shop-domain` (or `x-shopify-shop-domain`) header. No credentials, tokens, or the `client_secret` need to be stolen — the gem's own verification logic never checks the header against the signature.

### Recommendation
Include the `shop-domain` (and ideally `topic`, `webhook-id`, `api-version`) header values in the signed material that `to_signable_string` protects, or otherwise cryptographically bind them to the verified payload before they are surfaced to handlers via `WebhookMetadata`. At minimum, the recomputed HMAC input should incorporate the shop identifier, and `Registry.process` should reject any request whose header-derived shop cannot be tied to the signature, rather than trusting header values wholesale after only verifying the body.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com`.
2. Shopify sends a legitimate webhook (e.g. `orders/create`) to the app's webhook endpoint with a body `B` and header `X-Shopify-Hmac-Sha256: HMAC(secret, B)` and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker (who controls their own inbound traffic/proxy) captures `B` and the valid HMAC header, then re-POSTs the identical body/HMAC pair to the same endpoint but with `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B)` — unchanged — so validation succeeds [5](#0-4) .
5. The forged `shop` header flows unchecked into `WebhookMetadata.new(... shop: request.shop ...)` [6](#0-5) , causing the host application's handler to process attacker-controlled data as if it originated from `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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
