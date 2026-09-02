This confirms the vulnerability: `Registry.process` validates the HMAC only against `@raw_body`, and separately trusts the `shop-domain` header without any cryptographic binding between the two.This confirms the finding. The `Webhooks::Request#hmac` validation (via `Utils::HmacValidator.validate`) signs and verifies only `@raw_body` (`to_signable_string` returns `@raw_body`), while `shop` is read from the `x-shopify-shop-domain`/`shopify-shop-domain` header, completely outside the HMAC-covered content. `Registry.process` passes this unauthenticated `request.shop` value straight into `WebhookMetadata` and to the host app's handler, which the docs explicitly show being used as the tenant identifier (`shop_domain: data.shop`) for storage/lookups.

### Title
Webhook Shop-Domain Header Is Not Bound to the HMAC Signature, Enabling Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `Utils::HmacValidator.validate` verifies the HMAC exclusively over that body. The `shop` value, read from the `x-shopify-shop-domain` (or `shopify-shop-domain`) header, is never included in the signed content. `Registry.process` accepts the request once the body's HMAC checks out and then feeds the unauthenticated header-derived `shop` value into `WebhookMetadata`, which host apps use to identify which tenant/shop the webhook belongs to.

### Finding Description
In `lib/shopify_api/webhooks/request.rb`:
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
...
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

And in `lib/shopify_api/webhooks/registry.rb`:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [2](#0-1) 

`Utils::HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against the received `hmac`: [3](#0-2) 

Since `to_signable_string` is only `@raw_body`, the identity binding the report's bug class calls out — "a field acted on but not covered by the HMAC" — is broken here: the `shop` header used to identify the tenant is not part of what's cryptographically verified. Critically, Shopify's webhook HMAC secret is the app's single global `api_secret_key`, shared across every installed shop, not a per-shop secret. This means any `(raw_body, hmac)` pair that validates for one shop's webhook will validate identically regardless of which `shop-domain` header accompanies it — the signature says nothing about which shop the data belongs to.

### Impact Explanation
This breaks the equality that should hold: `shop authenticated == shop bound to the verified payload`. In a multi-tenant app (one endpoint serving many merchants), a merchant who legitimately receives their own valid webhook deliveries (body + HMAC, both visible to them since it's delivered to their own server) can replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting a different value in the `shop-domain` header. The HMAC check still passes (it only checks the body), and the host application's handler — per this gem's own documented usage pattern (`shop_domain: data.shop`) — will process/store that data as if it belongs to the victim shop. This is a cross-tenant data confusion/injection vector reachable by any existing merchant of a multi-tenant app, without needing the `api_secret_key`, an access token, or any privileged access — satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
High likelihood for any host app built on this gem the way the documentation instructs: the docs literally show `shop_domain: data.shop` used to route/attribute data. Any merchant already installed on a multi-tenant instance of the app can capture their own legitimately-signed webhook payloads (no secret needed) and replay them at the same public endpoint with a forged `shop-domain` header value.

### Recommendation
Bind the shop domain (and ideally other identifying headers such as topic and API version) into the signed content, or otherwise cryptographically tie the header-derived `shop` to the verified body — e.g., include `shop`, `topic`, and `webhook_id` in `to_signable_string`, or require the host application to cross-check `request.shop` against a known/registered shop list keyed by a value derived from validated session state rather than trusting the header outright. At minimum, document prominently that `request.shop` is unauthenticated and must not be used as a sole tenant-identity key without additional verification (e.g., checking it against the shop associated with the specific webhook subscription/ID via the Admin API).

### Proof of Concept
1. App merchant A has webhooks registered and receives a legitimate webhook delivery at their configured endpoint with headers `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, and some `raw_body`.
2. Attacker (merchant A, or anyone who intercepts/replays this request) resends the exact same `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `shop-b.myshopify.com` (the victim tenant).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `raw_body` only — this still matches the (unchanged) `hmac` header, so validation succeeds: [4](#0-3) 
4. `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` is invoked with `shop: "shop-b.myshopify.com"`, even though the body/topic/webhook_id actually belong to shop A — the host application processes/stores merchant A's order/customer data under merchant B's identity, or triggers shop-B-scoped side effects using attacker-controlled body content that was never actually signed for shop B.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
