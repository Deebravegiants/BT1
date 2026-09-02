Confirmed: `Webhooks::Request#to_signable_string` returns only `@raw_body`, and `hmac` is verified solely against that body via `Utils::HmacValidator.validate` [1](#0-0) , while `shop` is read straight from the unauthenticated `shopify-shop-domain` header and never included in the signed payload [2](#0-1) . `Registry.process` then trusts `request.shop` as the tenant identity when dispatching the webhook to the handler [3](#0-2) , and the HMAC secret (`Context.api_secret_key`) is shared across all shops of the app rather than being shop-specific [4](#0-3) .

### Title
Webhook `shop` identity not bound by HMAC allows cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` authenticates a webhook solely by validating the HMAC over the raw request body, but the `shop` field used downstream as the tenant identifier is taken from an HTTP header that is not covered by that signature.

### Finding Description
`Utils::HmacValidator.validate` computes and compares the HMAC using `verifiable_query.to_signable_string`, which for `Webhooks::Request` is defined as just `@raw_body` [1](#0-0) . The `shop` accessor, however, is derived independently from the `shopify-shop-domain`/`x-shopify-shop-domain` header [2](#0-1) , which plays no role in the signable string and is therefore never authenticated.

`Registry.process` validates the HMAC and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler as the tenant key [3](#0-2) :
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
end
```
Because the secret used for HMAC computation (`Context.api_secret_key`) is a single, app-wide secret shared across every shop that has installed the app, not a per-shop secret [4](#0-3) , a valid `(raw_body, hmac)` pair obtained for one shop remains cryptographically valid when replayed with a different `shopify-shop-domain` header value. This breaks the intended identity binding `authenticated_shop == request.shop`: the HMAC only proves "this body was produced with this app's secret," not "this body came from this specific shop."

### Impact Explanation
Any merchant who has installed the vulnerable app on their own store (i.e., any unprivileged attacker who can self-install a free/dev app) can generate arbitrary webhook events on their own shop (e.g., `customers/data_request`, `orders/create`, `app/uninstalled`) and obtain a genuinely valid `hmac-sha256` header for that body from Shopify. By replaying that exact body/HMAC pair to the app's webhook endpoint while substituting a victim shop's domain in the `shopify-shop-domain` header, the attacker's request passes `Registry.process`'s HMAC check and is delivered to the handler tagged as belonging to the victim shop. This is a cross-tenant identity confusion: attacker-controlled data is processed under another tenant's identity, which can corrupt per-shop state, trigger unauthorized actions (e.g., forced redaction/uninstall flows) or leak/attribute data across tenant boundaries in the host application, i.e., a cross-tenant access vulnerability.

### Likelihood Explanation
Exploitation only requires the ability to install the app on a shop the attacker controls (self-service on Shopify) and the ability to send an arbitrary HTTP POST with custom headers to the app's public webhook endpoint — no access to `api_secret_key`, tokens, or victim credentials is needed. The shared-secret design makes the forged header trivially swappable while the signature remains valid.

### Recommendation
Bind the shop identity into the signed payload actually verified, e.g., include `shop-domain` (and ideally `webhook-id`/`topic`) in `to_signable_string`, or otherwise verify `request.shop` against a value obtained through a channel that is itself authenticated (such as a per-shop lookup keyed by an already-verified session/token), instead of trusting the raw header once only the body HMAC has been checked.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook event (e.g., `customers/data_request`) on their own shop; Shopify sends `POST /webhooks` with body `B` and header `shopify-hmac-sha256: HMAC(secret, B)`, `shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker replays the identical body `B` and `shopify-hmac-sha256` value to the app's webhook endpoint, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `@raw_body` only (`to_signable_string` returns `@raw_body`) and it matches, so validation succeeds [1](#0-0) .
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload originated from the attacker's own shop [5](#0-4) .

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
