This confirms the finding: `Registry.process` verifies only the raw body via HMAC and then trusts `request.shop` (an unauthenticated header) to route the payload as `WebhookMetadata#shop`, which the documented app pattern (`docs/usage/webhooks.md:26`) uses directly as the tenant identifier (`shop_domain: data.shop`) for job dispatch/storage lookups.

### Title
Webhook `shop-domain` header is trusted for tenant identity without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating an HMAC over the raw request body only, then uses a separate, unauthenticated header (`shop-domain`) as the tenant/shop identity passed to the app's handler. Because the signature never covers the shop identity field, the two values are not cryptographically bound together, letting anyone who possesses one valid `(body, hmac)` pair (which they can obtain legitimately from their own store's webhook deliveries, since the signing secret is the app's single shared `client_secret` for all installs) relabel that payload as belonging to any other shop.

### Finding Description
`Registry.process` gates all webhook handling on `Utils::HmacValidator.validate(request)`: [1](#0-0) [1](#0-0) 

The HMAC's signable content is defined by `Webhooks::Request#to_signable_string`, which returns only `@raw_body`: [2](#0-1) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from attacker-suppliable HTTP headers with no cryptographic linkage to the signed body: [3](#0-2) [4](#0-3) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (the body) and the app's `api_secret_key`: [5](#0-4) 

The identity binding that should hold is: `hmac_valid(body, secret) == true` implies `shop-domain header == the shop that actually generated body`. Instead, the equality that is actually enforced is only `hmac_valid(body, secret) == true`, with `shop` accepted unconditionally as long as the header is present. The `shop` value is then forwarded verbatim into `WebhookMetadata`, which is exactly what the documented handler pattern uses to key persistence/queueing by tenant: [6](#0-5) [7](#0-6) 

Because the `api_secret_key`/`client_secret` used to sign webhooks is shared by the app across every installing shop (not per-shop), any merchant who installs the app can generate real, validly-signed `(body, hmac)` pairs simply by triggering ordinary events in their own store (e.g. creating an order, whose body content they can influence via order notes/line item titles/custom attributes). Since the header carrying `shop-domain` is outside the signed content, that same attacker can submit an HTTP request directly to the app's webhook endpoint with the legitimately-signed body/hmac pair but an arbitrary `x-shopify-shop-domain` (or `shopify-shop-domain`) header naming a different, victim shop that also uses the app.

### Impact Explanation
This crosses a tenant boundary: an unprivileged app user (any merchant who installs the app) can cause the app's webhook handler to process attacker-controlled data under the identity of a different, unrelated shop, because the gem asserts webhook authenticity (`InvalidWebhookError` is only raised on HMAC mismatch) while `data.shop` is fully attacker-controlled. Any host application that follows the documented pattern of using `data.shop` to key which tenant's records/jobs are affected is exposed to cross-tenant data injection/confusion (e.g. fake `orders/create`, `app/uninstalled`, or `customers/data_request` events attributed to a victim shop). This matches the "cross-tenant access" class of impact.

### Likelihood Explanation
Likelihood is high for any app that has more than one active install: the attacker needs no credentials beyond installing the app themselves (an ordinary, unprivileged flow), and the payload is entirely decoupled from the identity header by design in `Request#to_signable_string` and `Request#shop`. No secret material, TLS interception, or social engineering is required.

### Recommendation
Bind the shop identity to the signed payload before trusting it: either include the shop domain in the HMAC-signed content, or independently corroborate the header-provided `shop` against server-side state (e.g. only accept a `shop` value for which the app currently holds a webhook registration/session, matched to the specific `webhook_id`) rather than trusting the raw header unconditionally once body-HMAC validation passes.

### Proof of Concept
1. App is installed on `victim-shop.myshopify.com` and `attacker-shop.myshopify.com`, both signed with the same `api_secret_key`.
2. Attacker triggers a real webhook delivery for their own shop (e.g. `orders/create`) and captures the raw body `B` and its `x-shopify-hmac-sha256` value `S` (a validly-signed pair, since Shopify itself signs it with the shared secret).
3. Attacker POSTs directly to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: S`, but header `x-shopify-shop-domain: victim-shop.myshopify.com` and `x-shopify-topic`/`x-shopify-webhook-id` of choice.
4. `ShopifyAPI::Utils::HmacValidator.validate` returns `true` (it only checks `B` against `S`), so `Registry.process` calls the app's handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"` even though the payload never originated from that shop, per `lib/shopify_api/webhooks/registry.rb:188-199` and `lib/shopify_api/webhooks/request.rb:15-38`.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
