### Title
Webhook `shop`/`topic` identity is trusted from unauthenticated HTTP headers while the HMAC only signs the raw body - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented to "verify the request did indeed come from Shopify," but the HMAC it checks only binds the request *body*. The `shop` (and `topic`) identity that the app dispatch logic and handler code rely on come from HTTP headers that are never covered by that signature, so they can be freely rewritten by anyone able to relay a validly-signed body to the endpoint.

### Finding Description
`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`, and for `Webhooks::Request` that method returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id` and `api_version` are all read straight from HTTP headers with no HMAC coverage: [2](#0-1) 

`Registry.process` validates only the body HMAC, then dispatches on the unauthenticated `topic` header and hands the unauthenticated `shop` header straight to the app's handler as trusted identity data: [3](#0-2) 

The identity binding that should hold is: `shop header == shop that produced/authorized this signed body`. Before an attacker's request, that equality happens to hold because Shopify sets both consistently. After the attacker's request (same valid `raw_body`+HMAC pair, but with the `shopify-shop-domain` and/or `shopify-topic` headers swapped to an arbitrary value), the equality no longer holds, yet `HmacValidator.validate` still returns `true` and `Registry.process` proceeds to call the handler with the attacker-chosen `shop`/`topic` (`WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`). This mirrors the report's bug class exactly: a field that downstream logic acts on (`shop`/`topic`) is not part of the data actually covered by the cryptographic check (only `raw_body` is).

The docs explicitly promise this method "will verify the request did indeed come from Shopify," which overstates what is actually checked and encourages apps to trust `data.shop`: [4](#0-3) [5](#0-4) 

### Impact Explanation
Any party who can obtain one legitimately-signed `(raw_body, hmac)` pair for the app's registered secret — e.g., by installing the app on their own store and capturing a webhook Shopify sends them — can replay that exact body to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain (or substituting `shopify-topic` to invoke a different handler than the one the body was originally generated for). Because `Registry.process` only checks the body HMAC, the forged request passes validation and the handler executes believing the data belongs to the victim shop/topic. If the host application uses `data.shop` to key per-tenant database writes, authorization decisions, or to trigger tenant-specific side effects (a common, gem-encouraged pattern per the docs example `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), this enables cross-tenant data confusion/injection — data attributed to shop A can be forced to appear as belonging to shop B. This satisfies the "cross-tenant access" High/Critical impact category, since no session, access token, or `client_secret` is required by the attacker — only ownership of any one shop where the app is installed (an unprivileged/low-privilege actor relative to the victim tenant).

### Likelihood Explanation
Moderate-to-high: the prerequisite is trivial for anyone who can install the target app on a shop they control (many apps are freely installable on any development or trial store), after which capturing at least one valid webhook body/HMAC pair and replaying it with modified headers requires no special access, no leaked credentials, and no privileged account — it is a plain unauthenticated HTTP request to the app's public webhook callback URL. The gem's own documentation encourages exactly the trust pattern (`data.shop`) that makes this exploitable.

### Recommendation
Do not treat headers as authenticated. Either:
- Cryptographically bind `shop`, `topic`, and `webhook_id` into the signed material checked by `HmacValidator` (mirroring how Shopify actually can be configured, or by requiring the app to cross-check `data.shop` against a previously known/authorized session for that shop before trusting it), or
- Update documentation to explicitly state that only the raw body is authenticated by `process`, and instruct implementers to independently verify `data.shop` against their own session/install records rather than trusting the header value for tenant-sensitive logic.

### Proof of Concept
1. App X is installed on attacker-controlled store `attacker.myshopify.com`. Shopify sends a legitimate webhook: `raw_body = B`, header `x-shopify-hmac-sha256 = HMAC(secret, B)`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`.
2. Attacker captures this exact request (e.g., via a proxy they control in front of their own store's callback receiver, or simply because it's their own traffic).
3. Attacker replays the identical `raw_body` and `hmac` header to the same public webhook endpoint of App X, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
4. `Utils::HmacValidator.validate` in `Registry.process` recomputes the HMAC over `raw_body` only — it matches, so validation succeeds: [6](#0-5) 
5. The handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: parsed(B), ...)`, and any tenant-scoped side effect the app performs (e.g., enqueuing a job keyed by `shop_domain: data.shop` as shown in the gem's own docs example) is now executed under the victim's identity using attacker-controlled body content.

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

**File:** docs/usage/webhooks.md (L10-18)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
