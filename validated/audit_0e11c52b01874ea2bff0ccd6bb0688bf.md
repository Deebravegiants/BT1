### Title
Webhook shop attribution is not covered by the HMAC signature, allowing cross-tenant handler invocation - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC only over the raw request body (`to_signable_string` returns `@raw_body`), while the `shop`, `topic`, `api_version`, and `webhook_id` values that `Registry.process` uses to dispatch and attribute the payload are read from unauthenticated HTTP headers that are never included in the signed material.

### Finding Description
`Utils::HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to `verifiable_query.hmac` [1](#0-0) . For webhooks, `to_signable_string` is defined as simply `@raw_body` [2](#0-1) , meaning the HMAC only binds the JSON body bytes. The `shop` value, however, is read directly from the `shopify-shop-domain` / `x-shopify-shop-domain` header with no cryptographic binding at all [3](#0-2) .

`Registry.process` validates the HMAC and then dispatches to the app's handler using `request.shop` taken straight from that header: [4](#0-3) 

The identity binding that should hold is: `shop attributed to the webhook == shop whose secret validated the HMAC`. Because `shop` is not part of `to_signable_string`, this equality is never checked — only "these body bytes were signed by *a* valid secret for *some* shop" is proven, not "this body belongs to *this* shop." In a single-tenant app configuration this is low-impact since there's only one shop; but any app that operates as multi-tenant/proxy (forwarding raw webhook body + hmac + headers between processes, load balancers, or reverse proxies that rewrite/re-attach shop headers) allows an attacker who can influence the `shop-domain` header — without knowing `api_secret_key` — to make a validly-signed body from Shop A be processed and attributed to Shop B in the handler (`WebhookMetadata#shop`), which downstream logic (data storage, entitlement toggling, uninstall processing, GDPR deletion, etc.) typically keys off of.

Additionally, since `shopify_header` reads from a header dictionary supplied by whatever web framework surrounds the gem, and the header is never covered by HMAC, this is a case where "a field acted on (shop) but not covered by the HMAC" as called out in the report's bug-class hint.

### Impact Explanation
If a caller (proxy, queue consumer, or replay path) can present a raw body/HMAC pair captured for one shop alongside a different shop-domain header, `Registry.process` will treat and dispatch data as belonging to the second shop while accepting a signature computed for the first. Any handler logic that trusts `WebhookMetadata#shop` for tenant identification (common pattern, e.g., writing GDPR-webhook payloads, uninstall cleanup, or billing state per shop) can then perform cross-tenant data mutation from mismatched signatures. This matches "cross-tenant access" impact.

### Likelihood Explanation
Exploitation requires a component in front of, or forwarding into, the gem's `Registry.process` call that lets header and body diverge (e.g., a shared HMAC-secret proxy fan-out, or any deployment that stores/replays raw body+hmac across shop boundaries) — this is not exploitable from a bare unauthenticated internet request against a single endpoint bound to one shop's config, since `Context.api_secret_key` is fixed per-process. Likelihood is therefore moderate and configuration-dependent rather than trivially exploitable by every unprivileged caller.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signed material (or otherwise cryptographically bind them, e.g. by validating the header against the signed body via a combined canonical string) so `HmacValidator.validate` proves both "the body is authentic" and "this shop/topic attribution is authentic," rather than only the former.

### Proof of Concept
Not independently exploitable purely over the internet against a single-tenant deployment (requires a multi-tenant forwarding/proxy component that lets `shop-domain` header and signed body diverge), so this is reported as a design gap rather than a standalone remotely-triggerable exploit:
1. Capture a legitimate webhook body `B` and its valid `X-Shopify-Hmac-Sha256` header signed for `shop-a.myshopify.com`.
2. Replay `B` + same HMAC header, but with `X-Shopify-Shop-Domain: shop-b.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` returns `true` (body unchanged) [1](#0-0) , and `Registry.process` invokes the handler with `shop: "shop-b.myshopify.com"` [5](#0-4) , causing shop-A data to be processed under shop-B's identity.

### Citations

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
