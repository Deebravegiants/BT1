### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC of the raw request body. The `shop` value that identifies which merchant/tenant the webhook belongs to is read from an HTTP header that is never included in the HMAC-signed payload. Any actor who can obtain one legitimately-signed webhook (e.g. by installing the app on their own store) can replay that exact signed body while substituting the `X-Shopify-Shop-Domain` header for a victim shop, and the gem will accept it as authentic data for the victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all parsed straight from headers without being part of the signed material: [2](#0-1) 

`Utils::HmacValidator.validate_signature` computes the HMAC over `verifiable_query.to_signable_string` (the body only) using the app's shared `api_secret_key`, and compares it against the received signature: [3](#0-2) 

`Registry.process` gates the entire webhook pipeline on this body-only HMAC check, then forwards the unauthenticated `request.shop` value directly to the app's handler as the tenant identity: [4](#0-3) 

The identity binding that should hold is: `shop` (used to route/attribute the webhook data to a tenant) `==` `shop` (covered by the HMAC that proves the payload actually originated from Shopify for that shop). Because `shop` is excluded from `to_signable_string`, this equality is never enforced — the HMAC proves only "this app's secret signed this body," not "this body belongs to this shop." Since the API secret key is shared across all shops that install the same app (it's a per-app secret, not per-shop), any installer of the app can capture a validly-signed webhook body for their own shop and replay it with a different `shop-domain` header value.

### Impact Explanation
This breaks the shop-authenticated-vs-shop-attributed binding described in scope, resulting in cross-tenant data injection: an attacker who installs the target app on their own (attacker-controlled) store can generate arbitrary genuine-looking webhook payloads (e.g., `orders/create`, `app/uninstalled`, `customers/data_request`) signed with a valid HMAC, then replay them to the app's public webhook endpoint while swapping the shop-domain header to a victim shop the attacker does not own. `ShopifyAPI::Webhooks::Registry.process` will accept the payload as authentic (HMAC passes) and hand it to the app's handler tagged with the victim's shop, letting the attacker inject or forge data under another tenant's identity — a cross-tenant access impact.

### Likelihood Explanation
The attacker only needs to be able to install the target app on any shop they control (a normal, unprivileged action available to any internet user who can create a Shopify dev/trial store) and to control an HTTP client capable of sending arbitrary headers to the app's public webhook URL. No access token, `client_secret`, or privileged account is required — the HMAC verification path (`HmacValidator.validate` / `Registry.process`) is exactly the code path exposed to internet-facing webhook endpoints.

### Recommendation
Bind the tenant identity into the signed material used for verification, not just the raw body:
- Include the `shop-domain` (and ideally `topic`/`webhook-id`) header values as part of what is authenticated, e.g. by requiring callers to additionally verify the shop against a per-shop-registered webhook secret or against known installed shops, or
- After the HMAC check succeeds, cross-check `request.shop` against an independent, authenticated source of truth (e.g., confirm the shop has a currently valid stored session/access token) before invoking the handler, so a shop with no legitimate relationship to the app/session store cannot be impersonated via header manipulation.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, a shop they fully control.
2. Shopify sends a webhook (e.g. `orders/create`) to the app's endpoint with a body `B` and header `X-Shopify-Hmac-Sha256: HMAC(secret, B)` and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker captures `B` and its valid HMAC value.
4. Attacker replays a POST to the same webhook endpoint with identical body `B` and identical HMAC header, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses the forged shop header; `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the (shop-independent) HMAC: [5](#0-4) 
6. The app's registered handler executes with `WebhookMetadata.shop == "victim-shop.myshopify.com"`, causing the app to process attacker-supplied data as if it came from the victim tenant.

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
