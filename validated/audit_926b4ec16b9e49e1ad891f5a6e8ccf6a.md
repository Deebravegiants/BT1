This confirms the finding. The gem explicitly documents `Registry.process` as verifying "the request did indeed come from Shopify" (`docs/usage/webhooks.md:125`), and passes `data.shop` from the unverified header directly to the app's handler (`lib/shopify_api/webhooks/webhook_handler.rb:6-12`, `docs/usage/webhooks.md:14`, `docs/usage/webhooks.md:26` shows apps using `data.shop` as the tenant key). The HMAC only signs the raw body (`lib/shopify_api/webhooks/request.rb:36-38`), never the `shop`, `topic`, `webhook_id`, or `api_version` headers, so the gem's own guarantee is broken by its own root cause.

### Title
Webhook Shop-Domain Spoofing via HMAC That Only Covers the Body, Not the Shop Header - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook's authenticity solely by checking the HMAC over the raw request body [1](#0-0) . The `to_signable_string` used for that verification returns only `@raw_body`, deliberately excluding the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers [2](#0-1) . The `shop` value handed to the app's handler is read directly from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header [3](#0-2) . This breaks the identity binding: `shop header value == cryptographically authenticated shop`. Any attacker who runs their own Shopify store (an "unprivileged internet user" with respect to any *other* merchant) can install the target app, receive a genuinely-signed webhook for their own shop, and replay it to the app's webhook endpoint with only the `shop-domain` header swapped to a victim shop — the HMAC still validates because it never covered that header.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [4](#0-3) 
`hmac` is read from the `hmac-sha256` header, and `shop` is read separately from the `shop-domain` header — but `to_signable_string`, the value actually fed into `HmacValidator`, is just `@raw_body`: [5](#0-4) 

`HmacValidator.validate` computes `HMAC-SHA256(api_secret_key, verifiable_query.to_signable_string)` and compares it to the received signature [6](#0-5) . Because the signable string is only the body, the `shop` header is never part of what's authenticated.

`Registry.process` then trusts `request.shop` unconditionally once the HMAC (of the body) passes, and forwards it straight into the handler's `WebhookMetadata`: [7](#0-6) 

The `api_secret_key` is shared by the app across *all* installing shops (it is the app's client secret, not a per-shop secret) — see its use throughout `Context.api_secret_key` in `HmacValidator`. This means any shop that has installed the app can produce a body+HMAC pair that is valid under the app's single shared secret, then relabel the `shop-domain` header to any other shop's domain, and the app has no way to detect the substitution.

The gem's own documentation states this endpoint is expected to "verify the request did indeed come from Shopify" [8](#0-7) , and instructs consuming apps to treat `data.shop` as the authoritative tenant identifier (e.g. `shop_domain: data.shop`) [9](#0-8) , without any warning that this field is unauthenticated.

### Impact Explanation
This is a cross-tenant identity confusion: an attacker who is a legitimate but unprivileged installer of the app (e.g., using a free Shopify developer/trial store) can forge webhook deliveries that are processed by the app as if they originated from an arbitrary victim shop domain, including for mandatory compliance topics like `shop/redact` or `customers/data_request`/`customers/redact` (which the registry treats specially) [10](#0-9) . Depending on how the app keys its per-tenant state off `data.shop` (session lookup, data deletion, resync triggers, billing state), this enables cross-tenant data corruption, spoofed uninstall/redaction actions against a victim shop, or injection of attacker-controlled data into a victim's tenant record — satisfying the "cross-tenant access" criteria.

### Likelihood Explanation
Exploitation requires only: (1) the attacker installs the app on a store they control (trivial, unprivileged, no special access needed), (2) they capture one legitimate webhook delivery for their own shop (visible to them at their own registered endpoint, or they can trigger events like `orders/create` themselves), and (3) they replay the same body+HMAC to the target app's public webhook endpoint with a modified `shop-domain` header. No secrets, tokens, or victim cooperation are required.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is HMAC-verified, or otherwise cryptographically tie the claimed shop to the verified payload — e.g., include the shop domain in the signable string, or cross-check `request.shop` against a shop known to be associated with the specific `webhook_id`/subscription (Shopify's GraphQL Admin API can be queried to confirm a webhook subscription's shop). At minimum, document prominently that `WebhookMetadata#shop` is not authenticated by the HMAC and must not be trusted as a tenant identifier without additional verification.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" and has installed the target app.
# They receive (or trigger) a genuine webhook delivery, e.g.:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => "<genuine-hmac-for-body-below>", # valid HMAC(api_secret_key, raw_body)
  "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
  "x-shopify-webhook-id" => "attacker-controlled-id",
  "x-shopify-api-version" => "2024-01",
}
raw_body = '{"id": 1, "note": "hello"}'

# Attacker simply rewrites the shop-domain header and replays the SAME
# raw_body/hmac to the app's public webhook endpoint:
forged_headers = headers.merge("x-shopify-shop-domain" => "victim-shop.myshopify.com")

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
# HmacValidator.validate(request) still succeeds because to_signable_string == raw_body only.
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
# The app now processes attacker-controlled data attributed to the victim shop.
```

### Citations

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
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

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L24-26)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
