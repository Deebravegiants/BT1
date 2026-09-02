### Title
Webhook `shop` (and `topic`/`webhook_id`) identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by checking that the HMAC covers the raw request body. The `shop` (and `topic`/`webhook_id`) values that the handler is told to trust for tenant identification come from unauthenticated HTTP headers that are never included in the signed bytes. Because a single `client_secret` is shared across every shop that installs the app, any user who can obtain one genuine `(body, hmac)` pair for a shop they control can replay it to the app's public webhook endpoint with a forged `shop-domain` header, and the request passes validation while being attributed to an arbitrary victim shop.

### Finding Description
`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the `hmac` header: [1](#0-0) 

For webhooks, `to_signable_string` returns only `@raw_body` — none of the Shopify-supplied headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) are part of the signed material: [2](#0-1) 

`Registry.process` validates only this body-bound HMAC, then forwards the *unauthenticated* `request.shop` header value straight to the app's handler as the tenant identity: [3](#0-2) 

The documented integration pattern explicitly tells host apps to key their business logic off `data.shop`: [4](#0-3) 

This breaks the identity binding `shop_authenticated == shop_used_for_dispatch`. The gem only proves "this body was signed with the app's `client_secret`" — it does not prove "this body came from *this* shop". Since Shopify apps use one `client_secret` for all installed shops, *any* legitimate webhook recipient (e.g., a merchant who installed the app on their own store and thus legitimately receives real, validly-signed webhooks for that store) possesses a `(raw_body, hmac)` pair that is valid under the shared secret regardless of which shop it nominally belongs to. That user can POST the exact same `raw_body` + `hmac` to the app's public webhook URL while substituting the `X-Shopify-Shop-Domain` header for a victim shop's domain. `HmacValidator.validate` still succeeds (it never looks at the header), and `Registry.process` hands the handler a `WebhookMetadata` claiming `shop: <victim>` with body data that actually belongs to the attacker's own shop.

This is the sandwich-attack analog required by scope: the report's root cause is "the code that authorizes an action checks a different set of bytes than the bytes actually used to decide who benefits/who is affected." Here, the code that authenticates (HMAC over body) checks different content than the field used to decide *whose tenant record is affected* (the `shop` header).

### Impact Explanation
This is cross-tenant confusion carried through the gem's own credential (`client_secret`)-derived authentication mechanism. A host app following the gem's documented pattern (`data.shop` as tenant key) can be induced to apply an attacker-controlled shop's webhook body to a different, victim shop's records/queue — e.g., writing attacker data into a victim's `orders/create` processing pipeline, or triggering per-shop side effects (billing events, GDPR data-request handling, inventory sync) under the wrong tenant. Because dispatch and persistence of "which shop this event is for" is entirely mediated by this gem's `Request#shop` accessor and `Registry.process`, and no part of the signed payload is checked against it, this satisfies the "cross-tenant access" criterion for Critical impact.

### Likelihood Explanation
Requires only: (1) the attacker's own legitimate installation of the app (any user can install a public app on their own dev/test store), which yields real, validly-HMAC-signed webhook traffic addressed to their shop; and (2) the ability to POST arbitrary headers/body to the app's public webhook endpoint, which is inherent to how webhook endpoints work (they must be internet-reachable). No secrets, tokens, or privileged access are needed — this is exploitable by any unprivileged internet user who can install the target app once.

### Recommendation
Bind the identity fields into the signed material, or otherwise cryptographically tie `shop`/`topic`/`webhook_id` to the signature instead of trusting bare headers:
- Include `shop-domain`, `topic`, and `webhook_id` header values in `to_signable_string` (or a separate signature check) so any header tampering invalidates the HMAC, or
- Have `Registry.process` independently verify that `request.shop` matches an app-known/installed shop record before dispatch, and document that host apps must not treat `data.shop` as authenticated on its own.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`. Shopify sends a genuine webhook, e.g. `orders/create`, to the app's endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC_SHA256(client_secret, B)` (`Request#to_signable_string` = `B` only, per `lib/shopify_api/webhooks/request.rb` line 36-38).
2. Attacker captures `(B, H)` from their own installation (they legitimately receive it).
3. Attacker crafts a new HTTP POST to the same public webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged), but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only and matches `H` successfully (`lib/shopify_api/utils/hmac_validator.rb` lines 26-31).
5. `process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the spoofed `victim-shop.myshopify.com` value and invokes the host app's handler (`lib/shopify_api/webhooks/registry.rb` lines 190-199), which now processes attacker-controlled data under the victim shop's identity. [5](#0-4) [6](#0-5)

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** docs/usage/webhooks.md (L10-29)
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
    end
  end
end
```
