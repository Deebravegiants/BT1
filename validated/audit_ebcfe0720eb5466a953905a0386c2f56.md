### Title
Webhook shop-tenant identity spoofing due to HMAC covering only the raw body, not the `shop` header - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating an HMAC over the raw request body, then hands the caller-supplied `shop` header value — which is not part of the signed material — to the app's handler as trusted tenant identity. This breaks the intended equality `hmac_verified(body) == shop_is_authentic`, allowing a malicious merchant who legitimately installs the app (and thus legitimately receives correctly-HMAC'd webhooks under the app's single, shared `client_secret`) to relabel their own genuine webhook payload as belonging to a different (victim) shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
while `shop` is read directly from an HTTP header with no cryptographic binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` computes an HMAC-SHA256 over `to_signable_string` (i.e., the body only) and compares it to the `hmac` field using `OpenSSL.secure_compare`: [3](#0-2) 

`Webhooks::Registry.process` uses this same body-only HMAC check as the sole authentication gate, then immediately trusts `request.shop` (the unauthenticated header) to build `WebhookMetadata`, which is delivered directly to the host application's handler as the tenant identity for the event: [4](#0-3) [5](#0-4) 

The gem's own documentation instructs apps to route/scope work per-tenant directly off this `shop` field (`perform_later(topic: data.topic, shop_domain: data.shop, ...)`), confirming this is the intended and documented consumption pattern, not a host-app misuse: [6](#0-5) 

Critically, the webhook HMAC secret is the app's single `client_secret`, shared across *every* shop that installs the app — it is not per-tenant. This means any unprivileged user who installs the app on their own store can trivially obtain a raw body + valid HMAC pair (their own real webhook delivery) and replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header rewritten to any other shop's domain. Because `to_signable_string` never covers the shop header, the equality the code implicitly assumes — `hmac_valid(body) == shop_header_is_authentic` — does not hold, breaking the identity binding between "who the HMAC proves this came through" and "which tenant this event is attributed to."

### Impact Explanation
This is a cross-tenant data-injection vector: an attacker who is merely a legitimate (but malicious) merchant of a multi-tenant Shopify app can forge webhook events that the host application will process as belonging to another merchant's shop, since the gem supplies `request.shop` to the handler as trusted, HMAC-validated data when it is not. Depending on the host app's use of `data.shop` (e.g., looking up/creating shop-scoped records, updating another tenant's cached state, triggering shop-scoped side effects), this enables cross-tenant access/injection — meeting the Critical bar for cross-tenant access defined in scope.

### Likelihood Explanation
Likelihood is high for any app built on this gem following its documented pattern: the attacker requires only their own legitimate app installation (an unprivileged, ordinary merchant account) to obtain real signed webhook bodies, and needs only to replay the request with a modified shop header to a public-facing webhook endpoint — no access to the `client_secret`, access tokens, or any other privileged credential is required.

### Recommendation
Bind the shop domain to the HMAC-authenticated material, or otherwise independently verify tenant identity before trusting `request.shop`:
- Include the shop-domain (and ideally topic/webhook-id) header value inside the signed payload used for HMAC verification, rejecting requests where they were not part of what Shopify actually signed, or
- Cross-check the header `shop` against an authoritative record (e.g., verify the shop is currently registered/subscribed for that specific `webhook_id`/topic via the Admin API or persisted webhook registration state) before dispatching to the handler, or
- Document prominently, and enforce in code, that `data.shop` must never be trusted for tenant-scoping decisions without additional server-side verification against known webhook subscriptions.

### Proof of Concept
1. Attacker legitimately installs the target Shopify app on their own store `attacker.myshopify.com` and subscribes to a webhook topic (e.g., `orders/create`).
2. Shopify delivers a legitimate webhook to the app's endpoint with a body `B` and header `X-Shopify-Hmac-Sha256: HMAC(client_secret, B)` and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker captures this request (they control their own store and can trigger/observe deliveries) and replays it to the same app endpoint, only changing `X-Shopify-Shop-Domain` to `victim.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes `HMAC(client_secret, B)` — identical to before since `B` is unchanged — and returns `true` because it never considered the shop header. [7](#0-6) 
5. `Registry.process` passes the request straight through to the handler with `shop: "victim.myshopify.com"`, `topic`, and `body: B`, which the app treats as an authenticated event for the victim's tenant. [4](#0-3)

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

**File:** docs/usage/webhooks.md (L19-29)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
