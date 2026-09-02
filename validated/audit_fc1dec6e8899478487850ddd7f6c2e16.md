This confirms the finding. The webhook HMAC in `to_signable_string` (`lib/shopify_api/webhooks/request.rb:36-38`) covers only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated headers (`shopify_header`, lines 21-33), and the docs explicitly instruct developers to trust `data.shop` for tenant identification (`docs/usage/webhooks.md:14,26`) without any additional binding check in the gem itself.

### Title
Webhook shop-domain identity spoofing via HMAC that only covers body bytes, not headers - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` authenticates the body bytes but never binds the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers to that signature. Any party who can obtain one valid `(body, hmac)` pair for their own shop can replay it to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain` header, and `Registry.process` will accept it and hand the attacker-chosen shop identity to the handler as authenticated data.

### Finding Description
`Registry.process` gates webhook handling solely on `Utils::HmacValidator.validate(request)`: [1](#0-0) 

The HMAC check computes the signature exclusively over `to_signable_string`, which is defined as the raw body: [2](#0-1) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are parsed straight from HTTP headers with no cryptographic binding to the verified signature: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` only ever consult `verifiable_query.to_signable_string` (the body) and `verifiable_query.hmac`; the shop header never enters the computation: [4](#0-3) 

The identity equality that should hold is: `shop reported in WebhookMetadata == shop that produced the signed bytes`. Because the signature is computed over `raw_body` alone, this equality is not enforced — the `shop-domain` header is fully attacker-controlled once *any* valid `(raw_body, hmac)` pair is known, independent of which shop it originated from. Since `api_secret_key` is a single per-app secret shared across every merchant that installs the app (not shop-specific), any user who installs the app on their own store obtains a valid `(raw_body, hmac)` pair for a real event and can then POST that exact pair to the app's webhook URL while substituting the `x-shopify-shop-domain` header for a victim shop's domain. `Registry.process` still validates successfully and dispatches to the handler with `WebhookMetadata.shop` set to the attacker-chosen value: [1](#0-0) 

The gem's own documentation instructs developers to treat `data.shop` as the trusted tenant identifier (e.g., to enqueue per-shop jobs), reinforcing that this field is expected to be authenticated: [5](#0-4) 

### Impact Explanation
This breaks the tenant/shop identity binding that host applications rely on to route webhook data to the correct merchant record. An attacker who legitimately installs the app on a shop they control can forge a webhook that `Registry.process` accepts as coming from an arbitrary other shop domain, with attacker-controlled body content, since the body itself is what's signed and the attacker fully controls their own legitimate webhook bodies. Applications that key persistence, authorization, or side effects (e.g., updating order/inventory/customer data, triggering fulfillment, billing) off `WebhookMetadata.shop` can have that data associated with, or acted upon, an unrelated victim tenant — a cross-tenant impact.

### Likelihood Explanation
Reachable by any unprivileged internet user who can install the app on a store they control (a normal, self-service action for public apps) and then send a single crafted HTTP POST to the app's known webhook endpoint. No access to `api_secret_key`, access tokens, or privileged accounts of the victim is required.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) header in the signed payload used by `to_signable_string`, or otherwise cryptographically bind the shop identity to the HMAC before trusting `WebhookMetadata.shop` for tenant-scoped logic, so that swapping the header without resigning invalidates the HMAC.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and triggers a real event (e.g., `orders/create`), receiving a genuine webhook POST with body `B` and header `x-shopify-hmac-sha256: H` (valid because `HMAC(secret, B) == H`).
2. Attacker replays this exact request to the app's webhook endpoint, keeping body `B` and header `H` unchanged, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses `shop` as `"victim.myshopify.com"` from the header.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and compares to `H` — this still matches since neither depends on the shop header.
5. The registered handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: JSON.parse(B), ...)`, and any host logic keyed on `data.shop` now operates under the victim's identity using attacker-supplied body content.

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

**File:** docs/usage/webhooks.md (L10-26)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
```
