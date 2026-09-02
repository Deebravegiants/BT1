Based on the webhook processing pipeline, there's a genuine HMAC/shop binding gap worth reporting.### Title
Webhook `shop-domain` is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines `to_signable_string` to return only the raw HTTP body: [1](#0-0) 

The `shop` attribute, however, is read directly from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header: [2](#0-1) [3](#0-2) 

`Registry.process` validates the HMAC using `HmacValidator.validate(request)`, which in turn calls `to_signable_string` (body only) and compares it against the `hmac` header via `OpenSSL.secure_compare`: [4](#0-3) [5](#0-4) 

Once the HMAC check passes, `request.shop` (from the unauthenticated header) is trusted and passed directly into `WebhookMetadata`, which the host application's handler uses to attribute the event to a shop/tenant: [6](#0-5) [7](#0-6) 

The binding that should hold is: `shop attributed to the webhook event == shop that produced/authorized the signed payload`. Because the HMAC only signs the body and never the shop-domain header, this binding is broken: `hmac_valid(body) == true` does not imply `shop_header == originating_shop`. Any request whose body+HMAC pair is legitimately obtainable (e.g., a merchant who has the app installed on their own store and receives real webhooks for their own shop) can be resubmitted to the app's webhook endpoint with an arbitrary `shopify-shop-domain` header value naming a different, victim shop. The HMAC will still validate (it only checks the body against the app's shared `api_secret_key`), and the library will hand the handler a `WebhookMetadata` claiming the body belongs to the attacker-chosen victim shop.

### Impact Explanation
This is a cross-tenant identity-binding break: the value used by the host application to select per-shop credentials/state (`request.shop`) is not covered by the same authentication mechanism (`HmacValidator`) that vouches for the payload contents. A malicious but otherwise unprivileged merchant that has installed the app (and can therefore trigger and observe real, validly-signed webhook deliveries for their own store) can replay that valid (body, hmac) pair against the same shared endpoint while spoofing the `shop-domain` header to point at another merchant's shop. Any host application that follows this library's documented pattern — trusting `WebhookMetadata#shop` for tenant attribution without independently authenticating shop identity — will process or store data under the wrong tenant, resulting in cross-tenant data confusion/leakage of webhook-derived events. This aligns with the "Critical - cross-tenant access" impact category.

### Likelihood Explanation
Exploitation does not require access to `api_secret_key` or any Shopify credential theft: the attacker only needs their own working app installation (any merchant/unprivileged internet user can install a public app) to receive a legitimately signed webhook body+HMAC pair, then replays that exact payload to the shared webhook endpoint with a forged `shop-domain` header. No cryptographic secret needs to be recovered because the signature check never references the shop header at all. Likelihood is somewhat tempered because it requires the attacker to have their own valid app installation and to control/predict a webhook body they want attributed elsewhere (or accept whatever body their own store's events produce), and it depends on the host app trusting `request.shop`/`WebhookMetadata#shop` verbatim rather than cross-checking with its own session store — but the gem provides no protection against this and its own documentation/tests use `request.shop` as trusted tenant identity.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the signable string used for HMAC verification, or otherwise separately authenticate the `shop-domain` header against the resolved session, so that `HmacValidator.validate` fails whenever the shop attribute does not match the signed payload. At minimum, document prominently that `request.shop` is not authenticated by the HMAC and must be cross-validated by the host application against a known/installed shop list before being trusted for tenant attribution.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and receives a legitimate webhook delivery: raw body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC computed by Shopify using the app's shared `api_secret_key`), and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the exact same request to the app's webhook endpoint, but replaces the `x-shopify-shop-domain` header with `victim.myshopify.com`, keeping body `B` and HMAC `H` unchanged.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` builds successfully; `HmacValidator.validate` recomputes the signature only from `B` [1](#0-0)  and matches `H`, so `Registry.process` proceeds [8](#0-7) .
4. The handler receives `WebhookMetadata#shop == "victim.myshopify.com"` even though the payload actually originated from the attacker's own shop, breaking the shop-to-payload identity binding.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
