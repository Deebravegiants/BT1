## Title
Webhook Shop/Topic Identity Spoofing via HMAC That Only Covers the Raw Body - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` and `request.topic` — both derived from unauthenticated HTTP headers — to route and label webhook payloads, while the HMAC signature that "authenticates" the request only ever covers the raw request body. Any party who can obtain one validly-signed `(body, hmac)` pair (e.g., by triggering a real webhook delivery to their own installed store, since all shops share the same app `api_secret_key`) can replay that exact body/HMAC pair against the app's webhook endpoint while freely substituting the `shop-domain`, `topic`, and `webhook-id` headers, and the request will still pass verification.

### Finding Description
The HMAC verification entry point is `Utils::HmacValidator.validate`, which computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the received signature: [1](#0-0) 

For webhooks, `to_signable_string` is defined to return only the raw HTTP body: [2](#0-1) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from attacker-controllable HTTP headers, entirely outside the signed string: [3](#0-2) 

`Registry.process` verifies only the HMAC-over-body, then treats the unauthenticated `request.shop`/`request.topic` headers as trustworthy identity data to select the handler and populate the metadata passed to app code: [4](#0-3) 

The identity binding this breaks, stated as an equality:
`hmac_valid(body, secret) == true` is treated as implying `authenticated_shop == request.shop`, but in fact `to_signable_string(request) == raw_body` only, so `authenticated_shop` is never bound to anything — `request.shop` is fully attacker-controlled while the signature remains valid for that same body under any shop/topic/webhook_id header combination.

Because the app's `api_secret_key` (`Context.api_secret_key`) is a single, global secret shared across every shop that has installed the app, an unprivileged attacker who legitimately installs the app on their own shop can trigger a real webhook delivery (e.g. an `orders/create` event with attacker-chosen body content) and capture the resulting valid `(raw_body, X-Shopify-Hmac-SHA256)` pair. That pair remains valid under the shared secret regardless of which `shop-domain`/`topic`/`webhook-id` headers accompany it. The attacker can then POST the same body+HMAC directly to the app's public webhook endpoint with a forged `shop-domain` header naming a victim shop (also an app installer) and/or a forged `topic` header selecting a different handler than the one Shopify actually intended.

### Impact Explanation
This breaks the shop/tenant identity boundary that `Registry.process` and `WebhookMetadata` are relied upon to enforce: the app-level webhook handler receives `data.shop` it will treat as authenticated for a shop it does not actually correspond to, allowing an attacker-controlled body to be injected/attributed to another tenant, or a handler for a different topic to be invoked with attacker-influenced content. This is a cross-tenant confusion/injection primitive achievable purely by an unprivileged (but "legitimately installed") internet user with no access to the app's `client_secret`, refresh token, or any victim credential — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation only requires the attacker to be able to install the target app on a shop they control (a normal, low-privilege action for any Shopify merchant/developer) and to be able to reach the app's public webhook receiver endpoint, which by definition is internet-reachable. No secret material needs to be known or brute-forced; the attacker simply reuses a signature Shopify itself legitimately computed for their own webhook, capitalizing on the fact that headers are not bound into that signature.

### Recommendation
Bind the identity-carrying fields into the signed string (or otherwise cryptographically bind `shop`, `topic`, and `webhook_id` to the signature) instead of relying solely on `to_signable_string` returning the raw body. At minimum, `Webhooks::Request#to_signable_string` should incorporate the `shop-domain`/`topic`/`webhook-id` headers so that `HmacValidator.validate` fails whenever any of those headers are altered relative to what was actually signed, and `Registry.process` should not treat header-derived `shop`/`topic` as authenticated unless they are covered by the verified signature.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a legitimate, unprivileged action).
2. Attacker triggers a real webhook (e.g. by creating an order) and captures the delivered `raw_body` and `X-Shopify-Hmac-SHA256` header — both valid under the app's single shared `api_secret_key`.
3. Attacker POSTs to the app's webhook endpoint with the same `raw_body` and `hmac` header, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `X-Shopify-Topic`).
4. `Utils::HmacValidator.validate` succeeds because it only checks `HMAC(secret, raw_body)` [2](#0-1) ; `Registry.process` then invokes the registered handler with `shop: "victim-shop.myshopify.com"` [5](#0-4) , causing the app to process attacker-controlled data as if it originated from the victim tenant.

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
