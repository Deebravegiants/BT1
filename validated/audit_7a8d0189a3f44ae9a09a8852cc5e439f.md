### Title
Webhook `shop` (tenant) field is passed to app handlers unauthenticated by the HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` extracts the `shop`, `topic`, `api_version`, and `webhook_id` fields entirely from HTTP headers, while `Utils::HmacValidator` (invoked by `Registry.process`) only verifies the HMAC over the raw request body. None of the header-derived fields — most importantly `shop`, the tenant identifier passed to the app's `WebhookHandler#handle` — are bound to the signature. Any party capable of producing one valid `(body, hmac)` pair for the shared app `client_secret` can replay that pair with an arbitrary `shop-domain` header, and the gem will deliver it to the app as an authenticated webhook "from" a shop the attacker does not control.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `shop`, `topic`, `api_version`, and `webhook_id` are read straight from attacker-controllable HTTP headers with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` validates only the `hmac` (i.e., only the body) before dispatching: [3](#0-2) 

`Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string`, which for webhooks is the raw body only: [4](#0-3) 

The `shop` value extracted this way is placed directly into `WebhookMetadata`, the trust boundary the app-level handler relies on to know which tenant/store the event belongs to: [5](#0-4) [6](#0-5) 

Binding broken (as equality): the app's trust invariant is `verified_hmac_scope == tenant_identity_used_by_handler`. In reality the gem only enforces `verified_hmac_scope == raw_body`, while `tenant_identity_used_by_handler == request.shop` (an unauthenticated header). These two are not the same value, so `shop-domain` can diverge freely from what the HMAC actually attests to.

Because the `client_secret` used to sign webhooks is shared across every shop/tenant that installs the app (it is the app's secret, not a per-shop secret), any attacker who owns/operates one installed shop can legitimately receive real webhooks from Shopify for their own shop with a valid `(body, hmac)` pair, then replay that exact body+HMAC to the app's webhook endpoint while substituting a different value in the `X-Shopify-Shop-Domain` header. `HmacValidator.validate` will still return `true` (it never inspected the header), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event is from the victim shop.

### Impact Explanation
This breaks the shop/tenant identity binding that downstream app code relies on when a webhook is "verified." An app that trusts `WebhookMetadata#shop` (as the library encourages, since it's the only shop identifier surfaced after HMAC verification) to select which tenant's data/session/store record to mutate can be made to attribute attacker-supplied, attacker-controlled body content to an arbitrary victim shop — i.e., cross-tenant data injection/confusion despite passing "HMAC validation." This matches the Critical bucket ("cross-tenant access") because the confused identity crosses a tenant boundary using only a body+HMAC pair the attacker can legitimately obtain for their own installation, no leaked secret or privileged account required.

### Likelihood Explanation
Requires only that the attacker operate (or install the app on) one shop, receive a real webhook (trivial — trigger any subscribed event on their own store), and replay the captured request with a modified `shop-domain` header to the app's public webhook endpoint. No secrets, TLS interception, or privileged access are needed — it is exploitable by any unprivileged merchant/attacker who can install the app once.

### Recommendation
Bind the tenant/topic identity into the signed material, or otherwise cryptographically verify `shop-domain`/`topic`/`webhook-id` against the signed body (e.g., include them in the HMAC input, or require the caller to additionally verify shop identity against a per-shop stored offline session/access token before trusting `WebhookMetadata#shop`). At minimum, document prominently that `Registry.process`'s HMAC check only authenticates body integrity/authenticity of *an* app webhook, not the `shop` header, and that consuming applications must independently confirm the shop is one that has actually installed the app (e.g., cross-check against a known session) before acting on `WebhookMetadata#shop`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g. `orders/create`, with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for `B` under the shared `client_secret`).
2. Attacker resends this exact request to the app's webhook endpoint but changes the header:
   `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   keeping body `B` and `X-Shopify-Hmac-Sha256: H` unchanged.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (== `B`) only, matches `H`, and returns `true`. [7](#0-6) 
4. `Registry.process` builds `WebhookMetadata.new(... shop: request.shop ...)` with `shop == "victim-shop.myshopify.com"`, taken directly from the spoofed header, and invokes `handler.handle(data: ...)`. [5](#0-4) 
5. The app-level handler processes the attacker's order data believing it is authenticated data belonging to `victim-shop.myshopify.com`.

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
