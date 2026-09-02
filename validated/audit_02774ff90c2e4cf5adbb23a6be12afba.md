### Title
Webhook shop attribution is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's HMAC signature but then attributes the webhook to a shop taken from an unauthenticated header, breaking the equality "shop the HMAC-verified bytes belong to" == "shop the handler is told the data came from."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body: [1](#0-0) 
while `shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header with no cryptographic binding to the body: [2](#0-1) 
`Registry.process` validates the HMAC over that signable string (the body only), then immediately builds `WebhookMetadata` using `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version`, all sourced from unauthenticated headers, and hands it to the app's handler as trusted, verified data: [3](#0-2) 
The gem's own documentation reinforces the false binding, stating that `process` "will verify the request did indeed come from Shopify" and describing `data.shop` simply as "The shop domain of the webhook" with no caveat that it is unauthenticated: [4](#0-3) [5](#0-4) 

Because the HMAC only binds the body bytes, and `shop` is not part of the signable string, an attacker who controls a legitimately-installed shop (an unprivileged, self-serve action — install a free/dev store with the app) can capture one real Shopify-signed webhook (body + valid `hmac-sha256` header) for their own store, then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `shop-domain` header with a victim shop's domain. `Utils::HmacValidator.validate` still succeeds because it only checks the (unchanged) body against the secret: [6](#0-5) 
The handler then receives `WebhookMetadata` claiming the (attacker-controlled, but validly-signed) body belongs to the victim shop.

### Impact Explanation
This breaks the identity binding "shop == owner of the HMAC-verified body" and lets an unprivileged app installer attribute arbitrary signed webhook payloads to a different tenant (shop) of the same app. Any host application that keys per-tenant logic (e.g., looking up the victim's session/access token by `data.shop`, updating the victim's local records, billing, inventory sync, etc.) purely off the value the gem hands it will act on attacker-supplied content under the victim's identity — a cross-tenant access/confusion issue reachable purely through documented library usage, not by ignoring it.

### Likelihood Explanation
Requires only that the attacker operate their own shop with the target app installed (a normal, unprivileged action available to any merchant/developer) and be able to POST to the app's public webhook endpoint with custom headers — no access token, `client_secret`, or victim credentials are needed. The webhook body doesn't need to be modified at all, only the `shop-domain` header, so the attack is trivial to construct once one legitimate webhook has been captured.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-covered signable string, or otherwise cryptographically bind the shop attribution to the verified payload rather than trusting the unauthenticated header. At minimum, the documentation should clearly state that `data.shop` is unauthenticated and that consuming applications must independently verify it belongs to a shop with the app installed before using it for any tenant-scoped action.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw body and the valid `x-shopify-hmac-sha256` value Shopify sent.
2. Attacker POSTs the exact same body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this into a `Request` whose `to_signable_string` is the unmodified body [1](#0-0) , so `Utils::HmacValidator.validate` returns `true` [6](#0-5) .
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` [3](#0-2) , causing the host app to act on attacker-controlled data under the victim's tenant identity.

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

**File:** docs/usage/webhooks.md (L10-16)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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
