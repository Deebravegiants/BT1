This confirms the vulnerability pattern: `Webhooks::Request#hmac` is verified only against `to_signable_string`, which returns just `@raw_body` [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` values used by `Registry.process` to route and identify the tenant come from unauthenticated HTTP headers that are never included in the HMAC-signed payload [2](#0-1) . `Registry.process` validates the HMAC over the body only, then dispatches using `request.shop` from the header, and this shop value flows straight into the handler as tenant identity [3](#0-2) .

### Title
Webhook shop/topic identity headers are excluded from HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from only the raw request body [1](#0-0) , while the tenant-identifying `shop-domain`, `topic`, `webhook-id`, and `api-version` fields are read straight from HTTP headers with no cryptographic binding to that body or its HMAC [2](#0-1) . `HmacValidator.validate` only checks `to_signable_string` against the `hmac` value [4](#0-3) , so it never binds the headers.

### Finding Description
The equality that should hold is: `shop bound by HMAC == shop delivered to the handler`. Instead, `Registry.process` raises only if `Utils::HmacValidator.validate(request)` fails on the body, then immediately calls `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` using the unauthenticated header values [3](#0-2) . Since `hmac-sha256` is computed by Shopify (and independently by the app) purely over the JSON body, any valid `(body, hmac)` pair — for example one legitimately received by the app for its own installed shop — remains valid regardless of which `shop-domain`, `topic`, or `webhook-id` header values accompany it in a replayed/forged request to the app's webhook endpoint. An unprivileged holder of one legitimate webhook delivery (their own shop's install) can therefore submit that same body+HMAC with a different `x-shopify-shop-domain` header and have the app process it as if it came from a different, arbitrary shop.

### Impact Explanation
This breaks the tenant boundary the app relies on the gem to enforce: `WebhookMetadata#shop` is trusted by host applications to scope data access, deletion (e.g., `shop/redact`, `customers/redact`), or persistence per tenant. Forging the `shop` field lets an attacker cause the host app to act on/associate webhook payloads with a shop they don't own, i.e., cross-tenant data confusion, matching the report's "Critical - cross-tenant access" category.

### Likelihood Explanation
Requires only header manipulation on an HTTP request (no `client_secret`, no access token, no TLS interception) plus possession of one valid body/HMAC pair, obtainable from the attacker's own legitimately-installed shop. This is a directly reachable, code-level root cause in `lib/shopify_api/webhooks/request.rb` and `registry.rb`, not a host-application misuse.

### Recommendation
Bind the `shop-domain` (and ideally `topic`/`webhook-id`) header values into `to_signable_string`, or have `Registry.process` independently verify that the shop/topic embedded in the parsed body (if present) matches the header-derived values before dispatch, so the HMAC covers everything the handler treats as authoritative.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook delivery: raw body `B`, header `x-shopify-hmac-sha256: H` (valid for `B`), `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`.
2. Attacker replays a POST to the app's webhook endpoint with the same body `B` and same `H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because `to_signable_string` only returns `B`, unaffected by header changes [1](#0-0) .
4. `handler.handle` is invoked with `shop: "victim-shop.myshopify.com"` [5](#0-4) , causing the host app to process/attribute the payload to the victim shop.

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
